
using System;
using AetherEngine.TerraEngine.Interop;

namespace AetherEngine.TerraEngine
{
    public sealed class TerraEngineRuntime : IDisposable
    {
        private IntPtr handle = IntPtr.Zero;

        public bool IsCreated => handle != IntPtr.Zero;

        public static string GetAPIVersion()
        {
            TerraEngineStatus status =
                TerraEngineNative.TerraEngine_GetAPIVersion(
                    out uint major,
                    out uint minor,
                    out uint patch
                );

            if (status != TerraEngineStatus.Success)
                throw new InvalidOperationException(
                    "Failed to retrieve TerraEngine API version."
                );

            return $"{major}.{minor}.{patch}";
        }

        public TerraEngineRuntime()
        {
            TerraEngineStatus status =
                TerraEngineNative.TerraEngine_Create(out handle);

            if (status != TerraEngineStatus.Success ||
                handle == IntPtr.Zero)
            {
                handle = IntPtr.Zero;

                throw new InvalidOperationException(
                    $"TerraEngine creation failed: {status}"
                );
            }
        }

        public void Dispose()
        {
            if (handle == IntPtr.Zero)
                return;

            IntPtr oldHandle = handle;
            handle = IntPtr.Zero;

            TerraEngineStatus status =
                TerraEngineNative.TerraEngine_Destroy(oldHandle);

            if (status != TerraEngineStatus.Success)
                throw new InvalidOperationException(
                    $"TerraEngine destruction failed: {status}"
                );
        }
    }
}
