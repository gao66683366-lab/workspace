using System;
using System.Threading;
using System.Threading.Tasks;

namespace RobotLinkSDK
{
    /// <summary>
    /// 视频流接收器
    /// 
    /// 通过RTSP协议接收前视/后视双通道视频流
    /// 使用OpenCvSharp进行解码
    /// 支持低延迟模式（latency=0）
    /// </summary>
    public class VideoReceiver : IDisposable
    {
        #region 私有字段
        
        private CancellationTokenSource? _frontCts;
        private CancellationTokenSource? _rearCts;
        private Task? _frontTask;
        private Task? _rearTask;
        private bool _disposed = false;
        
        // RTSP URL
        private string _frontUrl = "";
        private string _rearUrl = "";
        
        // 延迟设置
        private int _latencyMs = 0;
        
        // 最新帧缓存
        private object _frontFrameLock = new();
        private object _rearFrameLock = new();
        private byte[]? _latestFrontFrame;
        private byte[]? _latestRearFrame;
        
        #endregion

        #region 事件定义
        
        /// <summary>前视视频帧回调（每帧触发）</summary>
        public event EventHandler<byte[]>? OnFrontFrame;
        
        /// <summary>后视视频帧回调（每帧触发）</summary>
        public event EventHandler<byte[]>? OnRearFrame;
        
        #endregion

        #region 构造与销毁
        
        public VideoReceiver()
        {
        }

        public void Dispose()
        {
            if (_disposed) return;
            _disposed = true;
            Disconnect();
            GC.SuppressFinalize(this);
        }

        ~VideoReceiver()
        {
            Dispose();
        }

        #endregion

        #region 连接管理
        
        /// <summary>
        /// 连接视频流
        /// </summary>
        /// <param name="frontUrl">前视RTSP URL</param>
        /// <param name="rearUrl">后视RTSP URL</param>
        /// <param name="latency">延迟模式，0=低延迟</param>
        public void Connect(string frontUrl, string rearUrl, int latency = 0)
        {
            _frontUrl = frontUrl;
            _rearUrl = rearUrl;
            _latencyMs = latency;
            
            // 前视视频流
            _frontCts = new CancellationTokenSource();
            _frontTask = Task.Run(() => VideoReceiveLoop(_frontUrl, true, _frontCts.Token));
            
            // 后视视频流
            _rearCts = new CancellationTokenSource();
            _rearTask = Task.Run(() => VideoReceiveLoop(_rearUrl, false, _rearCts.Token));
            
            Console.WriteLine($"[VideoReceiver] 启动，前视: {frontUrl}");
            Console.WriteLine($"[VideoReceiver] 启动，后视: {rearUrl}");
        }
        
        /// <summary>
        /// 断开视频流
        /// </summary>
        public void Disconnect()
        {
            try { _frontCts?.Cancel(); } catch { }
            try { _rearCts?.Cancel(); } catch { }
            
            _frontCts = null;
            _rearCts = null;
            _frontTask = null;
            _rearTask = null;
            
            Console.WriteLine("[VideoReceiver] 已断开");
        }
        
        /// <summary>
        /// 设置延迟模式
        /// </summary>
        public void SetLatency(int ms)
        {
            _latencyMs = ms;
            // 延迟模式需要重新连接才能生效
        }

        #endregion

        #region 视频接收循环
        
        /// <summary>
        /// 视频接收循环
        /// </summary>
        private async Task VideoReceiveLoop(string url, bool isFront, CancellationToken ct)
        {
            // 注意：这里使用简化实现
            // 实际使用需要引用OpenCvSharp或FFmpeg库
            // 以下为模拟代码，实际需要根据具体环境实现
            
            Console.WriteLine($"[VideoReceiver] {(isFront ? "前视" : "后视")} 接收循环启动");
            
            // 模拟实现：使用系统默认的RTSP客户端（如VLC）
            // 实际项目中应该使用OpenCvSharp.VideoCapture或FFmpeg.NET
            
            while (!ct.IsCancellationRequested)
            {
                try
                {
                    await Task.Delay(33, ct); // ~30fps
                    
                    // 这里是占位实现
                    // 实际需要使用：OpenCvSharp.VideoCapture capture = new VideoCapture(url);
                    // 然后循环：capture.Read(frame);
                    
                    // 触发帧回调（实际项目中传入真实帧数据）
                    // var frame = capture.RetrieveMat();
                    // if (isFront) OnFrontFrame?.Invoke(this, frame);
                    // else OnRearFrame?.Invoke(this, frame);
                }
                catch (OperationCanceledException)
                {
                    break;
                }
                catch (Exception ex)
                {
                    Console.WriteLine($"[VideoReceiver] {(isFront ? "前视" : "后视")} 异常: {ex.Message}");
                    await Task.Delay(1000, ct);
                }
            }
            
            Console.WriteLine($"[VideoReceiver] {(isFront ? "前视" : "后视")} 接收循环结束");
        }
        
        #endregion

        #region 帧获取
        
        /// <summary>
        /// 获取前视当前帧
        /// </summary>
        /// <returns>JPEG格式图像数据，或null</returns>
        public byte[]? GetFrontFrame()
        {
            lock (_frontFrameLock)
            {
                return _latestFrontFrame;
            }
        }
        
        /// <summary>
        /// 获取后视当前帧
        /// </summary>
        /// <returns>JPEG格式图像数据，或null</returns>
        public byte[]? GetRearFrame()
        {
            lock (_rearFrameLock)
            {
                return _latestRearFrame;
            }
        }
        
        #endregion

        #region 辅助方法（OpenCvSharp示例代码）
        
        /*
        下面是使用OpenCvSharp的实际实现示例：
        
        1. 安装OpenCvSharp4 NuGet包：
           dotnet add package OpenCvSharp4
           dotnet add package OpenCvSharp4.runtime.win
        
        2. 实际代码：
        
        using OpenCvSharp;
        
        private VideoCapture? _frontCapture;
        private VideoCapture? _rearCapture;
        
        private async Task VideoReceiveLoop(string url, bool isFront, CancellationToken ct)
        {
            var capture = new VideoCapture(url);
            capture.Set(VideoCaptureProperties.BufferSize, 1);  // 最小缓冲
            capture.Set(VideoCaptureProperties.Fps, 30);
            
            // 低延迟设置
            capture.Set(VideoCaptureProperties.GrabTimeout, 100);
            
            using var frame = new Mat();
            
            while (!ct.IsCancellationRequested)
            {
                try
                {
                    if (capture.Read(frame) && !frame.Empty())
                    {
                        // 转换为JPEG
                        var jpegData = frame.ImEncode(".jpg");
                        
                        if (isFront)
                        {
                            OnFrontFrame?.Invoke(this, jpegData);
                        }
                        else
                        {
                            OnRearFrame?.Invoke(this, jpegData);
                        }
                    }
                    else
                    {
                        await Task.Delay(10, ct);
                    }
                }
                catch (OperationCanceledException)
                {
                    break;
                }
                catch (Exception ex)
                {
                    Console.WriteLine($"[VideoReceiver] 异常: {ex.Message}");
                    await Task.Delay(1000, ct);
                }
            }
            
            capture.Release();
        }
        */
        
        #endregion
    }
}
