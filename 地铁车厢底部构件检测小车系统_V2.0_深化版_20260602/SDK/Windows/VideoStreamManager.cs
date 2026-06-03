using System;
using System.Diagnostics;
using System.IO;
using System.Net.Sockets;
using System.Threading;
using System.Threading.Tasks;

namespace RobotLinkSDK
{
    /// <summary>
    /// 视频流管理器 - RTSP H.264
    /// 
    /// 端口：554 (RTSP)
    /// 支持：前端相机、后端相机
    /// 集成FFmpeg解码
    /// </summary>
    public class VideoStreamManager : IDisposable
    {
        #region 私有字段
        
        private string _frontUrl = "";
        private string _rearUrl = "";
        private int _latencyMs = 0;
        
        private CancellationTokenSource? _frontCts;
        private CancellationTokenSource? _rearCts;
        private Task? _frontTask;
        private Task? _rearTask;
        
        private Process? _ffmpegFront;
        private Process? _ffmpegRear;
        
        private readonly object _lock = new();
        private bool _isConnected = false;
        
        // 帧回调
        public event EventHandler<byte[]>? OnFrontFrame;
        public event EventHandler<byte[]>? OnRearFrame;
        
        #endregion

        #region 属性
        
        public bool IsConnected => _isConnected;
        
        #endregion

        #region 构造与销毁
        
        public VideoStreamManager() { }

        public void Dispose()
        {
            Disconnect();
            GC.SuppressFinalize(this);
        }

        ~VideoStreamManager() => Dispose();

        #endregion

        #region 连接管理
        
        /// <summary>
        /// 连接视频流
        /// </summary>
        public void Connect(string frontUrl, string rearUrl, int latencyMs = 0)
        {
            _frontUrl = frontUrl;
            _rearUrl = rearUrl;
            _latencyMs = latencyMs;
            
            _frontCts = new CancellationTokenSource();
            _frontTask = Task.Run(() => VideoReceiveLoop(frontUrl, true, _frontCts.Token));
            
            _rearCts = new CancellationTokenSource();
            _rearTask = Task.Run(() => VideoReceiveLoop(rearUrl, false, _rearCts.Token));
            
            _isConnected = true;
            Console.WriteLine("[VideoStreamManager] 视频流已启动");
        }
        
        /// <summary>
        /// 异步连接（带超时）
        /// </summary>
        public async Task ConnectAsync(string frontUrl, string rearUrl, int latencyMs = 0, int timeoutMs = 5000)
        {
            Connect(frontUrl, rearUrl, latencyMs);
            
            var connectTask = Task.WhenAll(
                Task.Run(() => WaitForConnection(_frontCts!.Token)),
                Task.Run(() => WaitForConnection(_rearCts!.Token))
            );
            
            var timeoutTask = Task.Delay(timeoutMs);
            
            var completed = await Task.WhenAny(connectTask, timeoutTask);
            if (completed == timeoutTask)
                Console.WriteLine("[VideoStreamManager] 连接超时");
        }
        
        private async Task WaitForConnection(CancellationToken ct)
        {
            while (!ct.IsCancellationRequested && !_isConnected)
                await Task.Delay(100, ct);
        }
        
        /// <summary>
        /// 断开连接
        /// </summary>
        public void Disconnect()
        {
            _isConnected = false;
            
            try { _frontCts?.Cancel(); } catch { }
            try { _rearCts?.Cancel(); } catch { }
            try { _ffmpegFront?.Kill(); } catch { }
            try { _ffmpegRear?.Kill(); } catch { }
            
            _ffmpegFront = null;
            _ffmpegRear = null;
            _frontCts = null;
            _rearCts = null;
            _frontTask = null;
            _rearTask = null;
            
            Console.WriteLine("[VideoStreamManager] 视频流已断开");
        }

        #endregion

        #region 视频接收循环
        
        private async Task VideoReceiveLoop(string url, bool isFront, CancellationToken ct)
        {
            Console.WriteLine($"[VideoStreamManager] 启动{(isFront ? "前" : "后")}相机视频流: {url}");
            
            while (!ct.IsCancellationRequested)
            {
                try
                {
                    // 使用FFmpeg解码RTSP流
                    var ffmpeg = new Process
                    {
                        StartInfo = new ProcessStartInfo
                        {
                            FileName = "ffmpeg",
                            Arguments = $"-fflags nobuffer -flags low_delay -probesize 32 -analyzeduration 0 " +
                                      $"-rtsp_transport tcp -i "{url}" " +
                                      $"-f rawvideo -pix_fmt nv12 - " +
                                      $"-q:v 2 -r 25 -s 640x480 -",
                            RedirectStandardOutput = true,
                            RedirectStandardError = true,
                            UseShellExecute = false,
                            CreateNoWindow = true
                        },
                        EnableRaisingEvents = true
                    };
                    
                    if (isFront)
                        _ffmpegFront = ffmpeg;
                    else
                        _ffmpegRear = ffmpeg;
                    
                    ffmpeg.ErrorDataReceived += (s, e) =>
                    {
                        if (!string.IsNullOrEmpty(e.Data))
                            Console.WriteLine($"[Video] {e.Data}");
                    };
                    
                    ffmpeg.Start();
                    ffmpeg.BeginErrorReadLine();
                    
                    byte[] buffer = new byte[640 * 480 * 3 / 2];  // NV12格式
                    
                    while (!ct.IsCancellationRequested && !ffmpeg.HasExited)
                    {
                        int bytesRead = await ffmpeg.StandardOutput.BaseStream.ReadAsync(buffer, 0, buffer.Length, ct);
                        if (bytesRead > 0)
                        {
                            if (isFront)
                                OnFrontFrame?.Invoke(this, buffer);
                            else
                                OnRearFrame?.Invoke(this, buffer);
                        }
                    }
                    
                    ffmpeg.WaitForExit(1000);
                }
                catch (OperationCanceledException)
                {
                    break;
                }
                catch (Exception ex)
                {
                    if (!ct.IsCancellationRequested)
                    {
                        Console.WriteLine($"[VideoStreamManager] 视频流异常: {ex.Message}");
                        await Task.Delay(1000, ct);
                    }
                }
            }
        }
        
        #endregion

        #region 辅助方法
        
        /// <summary>
        /// 获取FFmpeg路径
        /// </summary>
        public static string FindFFmpegPath()
        {
            string[] paths = {
                "ffmpeg",
                "ffmpeg.exe",
                @"C:\ffmpeg\bin\ffmpeg.exe",
                @"./ffmpeg.exe"
            };
            
            foreach (var path in paths)
            {
                try
                {
                    var psi = new ProcessStartInfo
                    {
                        FileName = path,
                        Arguments = "-version",
                        RedirectStandardOutput = true,
                        UseShellExecute = false,
                        CreateNoWindow = true
                    };
                    using var process = Process.Start(psi);
                    if (process != null)
                    {
                        process.WaitForExit(1000);
                        if (process.ExitCode == 0)
                            return path;
                    }
                }
                catch { }
            }
            
            return "ffmpeg";  // 默认返回
        }
        
        #endregion
    }
}
