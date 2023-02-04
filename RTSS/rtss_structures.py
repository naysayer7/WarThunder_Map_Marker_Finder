from ctypes import Structure, c_char
from ctypes.wintypes import BYTE, DWORD, LARGE_INTEGER, LONG


class SharedMemoryStruct(Structure):  # v2.0 memory structure
    _fields_ = [
        ("dwSignature", c_char*4),
        # signature allows applications to verify status of shared memory

        # The signature can be set to:
        # "RTSS"	- statistics server"s memory is initialized and contains
        #             valid data
        # 0xDEAD	- statistics server"s memory is marked for deallocation and
        #             no longer contain valid data
        # otherwise	the memory is not initialized

        ("dwVersion", DWORD),
        # structure version ((major<<16) + minor)
        # must be set to 0x0002xxxx for v2.x structure

        ("dwAppEntrySize", DWORD),
        # size of RTSS_SHARED_MEMORY_OSD_ENTRY for compatibility with future versions

        ("dwAppArrOffset", DWORD),
        #  offset of arrOSD array for compatibility with future versions

        ("dwAppArrSize", DWORD),
        # size of arrOSD array for compatibility with future versions

        ("dwOSDEntrySize", DWORD),
        # size of RTSS_SHARED_MEMORY_APP_ENTRY for compatibility with future versions

        ("dwOSDArrOffset", DWORD),
        # offset of arrApp array for compatibility with future versions

        ("dwOSDArrSize", DWORD),
        # size of arrOSD array for compatibility with future versions

        ("dwOSDFrame", DWORD),
        # Global OSD frame ID. Increment it to force the server to update OSD
        # for all currently active 3D applications.

        # next fields are valid for v2.14 and newer shared memory format only

        ("dwBusy", LONG),
        # set bit 0 when you"re writing to shared memory and reset it when done
        # WARNING: do not forget to reset it, otherwise you"ll completely lock OSD updates for all clients

        # next fields are valid for v2.15 and newer shared memory format only

        ("dwDesktopVideoCaptureFlags", DWORD),
        ("dwDesktopVideoCaptureStat", DWORD * 5),
        # shared copy of desktop video capture flags and performance stats for 64-bit applications

        # next fields are valid for v2.16 and newer shared memory format only

        ("dwLastForegroundApp", DWORD),
        # last foreground application entry index

        ("dwLastForegroundAppProcessID", DWORD),
        # last foreground application process ID

        # next fields are valid for v2.18 and newer shared memory format only

        ("dwProcessPerfCountersEntrySize", DWORD),
        # size of RTSS_SHARED_MEMORY_PROCESS_PERF_COUNTER_ENTRY for compatibility with future versions

        ("dwProcessPerfCountersArrOffset", DWORD),
        # offset of arrPerfCounters array for compatibility with future versions (relative to application entry)

        # next fields are valid for v2.19 and newer shared memory format only

        ("qwLatencyMarkerSetTimestamp", LARGE_INTEGER),
        ("qwLatencyMarkerResetTimestamp", LARGE_INTEGER),

    ]


class SharedMemoryOSDEntry(Structure):  # OSD slot descriptor structure
    _fields_ = [
        ("szOSD", c_char * 256),
        # OSD slot text

        ("szOSDOwner", c_char * 256),
        # OSD slot owner ID

        # next fields are valid for v2.7 and newer shared memory format only

        ("szOSDEx", c_char * 4096),
        # extended OSD slot text

        # next fields are valid for v2.12 and newer shared memory format only

        ("buffer", BYTE * 262144),
        # OSD slot data buffer

        # next fields are valid for v2.20 and newer shared memory format only

        ("buffer", c_char * 32768),
        # additional 32KB extended OSD slot text
    ]


# process performance counter structure
class SharedMemoryProcessPerfCounterEntry(Structure):
    _fields_ = [
        ("dwID", DWORD),
        # performance counter ID, PROCESS_PERF_COUNTER_ID_XXX

        ("dwParam", DWORD),
        # performance counter parameters specific to performance counter ID
        # PROCESS_PERF_COUNTER_ID_D3DKMT_VRAM_USAGE_LOCAL	: contains GPU location (PCI bus, device and function)
        # PROCESS_PERF_COUNTER_ID_D3DKMT_VRAM_USAGE_SHARED	: contains GPU location (PCI bus, device and function)

        ("dwData", DWORD),
        # performance counter data
    ]
