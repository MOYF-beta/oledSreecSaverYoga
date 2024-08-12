import psutil
import platform

def check_psutil_function(func_name):
    try:
        # 调用 psutil 中的函数并返回结果
        func = getattr(psutil, func_name)
        result = func()
        print(f"{func_name}: {result}")
    except AttributeError:
        print(f"{func_name} function not found in psutil.")
    except (psutil.AccessDenied, psutil.NoSuchProcess, psutil.ZombieProcess) as e:
        print(f"Error accessing {func_name}: {str(e)}")
    except Exception as e:
        print(f"An error occurred with {func_name}: {str(e)}")

def main():
    print(f"System: {platform.system()} {platform.release()}")
    print(f"Processor: {platform.processor()}\n")

    psutil_functions = [
        'cpu_times', 'cpu_percent', 'cpu_times_percent', 'cpu_count', 
        'cpu_stats', 'cpu_freq', 'virtual_memory', 'swap_memory', 
        'disk_partitions', 'disk_usage', 'disk_io_counters', 'net_io_counters',
        'sensors_temperatures', 'sensors_fans', 'sensors_battery', 
        'boot_time', 'users'
    ]

    for func in psutil_functions:
        check_psutil_function(func)
        print("-" * 40)

if __name__ == "__main__":
    main()
