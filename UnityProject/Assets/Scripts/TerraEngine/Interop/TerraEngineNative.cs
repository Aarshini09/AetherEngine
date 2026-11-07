
using System;
using System.Runtime.InteropServices;

namespace AetherEngine.TerraEngine.Interop
{
    internal enum TerraEngineStatus
    {
        Success = 0,
        InvalidArgument = 1,
        OutOfMemory = 2
    }

    internal static class TerraEngineNative
    {
        private const string LibraryName = "TerraEngineNative";

        [DllImport(
            LibraryName,
            CallingConvention = CallingConvention.Cdecl,
            ExactSpelling = true
        )]
        internal static extern TerraEngineStatus TerraEngine_GetAPIVersion(
            out uint major,
            out uint minor,
            out uint patch
        );

        [DllImport(
            LibraryName,
            CallingConvention = CallingConvention.Cdecl,
            ExactSpelling = true
        )]
        internal static extern TerraEngineStatus TerraEngine_Create(
            out IntPtr outHandle
        );

        [DllImport(
            LibraryName,
            CallingConvention = CallingConvention.Cdecl,
            ExactSpelling = true
        )]
        internal static extern TerraEngineStatus TerraEngine_Destroy(
            IntPtr handle
        );
    }
}
