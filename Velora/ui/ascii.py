import math

def gradient_text(text, start_color, end_color):
    def rgb_interp(start, end, t):
        return tuple(int(start[i] + (end[i] - start[i]) * t) for i in range(3))
    lines = text.splitlines()
    gradient_lines = []
    total_chars = sum(len(line) for line in lines if line.strip())
    idx = 0
    for line in lines:
        colored_line = ""
        for char in line:
            if char.strip():  # Only color visible characters
                t = idx / (total_chars - 1)
                r, g, b = rgb_interp(start_color, end_color, t)
                colored_line += f"\033[38;2;{r};{g};{b}m{char}\033[0m"
                idx += 1
            else:
                colored_line += char
        gradient_lines.append(colored_line)
    return "\n".join(gradient_lines)

def gradient_text_selective(text, start_color, end_color, gradient_word, white_prefix=""):
    def rgb_interp(start, end, t):
        return tuple(int(start[i] + (end[i] - start[i]) * t) for i in range(3))
    
    lines = text.splitlines()
    result_lines = []
    
    for line in lines:
        if gradient_word in line and white_prefix in line:
            # Find the position of the prefix and gradient word
            prefix_start = line.find(white_prefix)
            word_start = line.find(gradient_word)
            
            if prefix_start != -1 and word_start != -1:
                # Split the line into parts
                before_prefix = line[:prefix_start]
                prefix_part = line[prefix_start:word_start]
                word_part = gradient_word
                after_word = line[word_start + len(gradient_word):]
                
                # Apply gradient only to the main ASCII art (before_prefix)
                colored_before = ""
                total_chars = sum(1 for char in before_prefix if char.strip())
                idx = 0
                for char in before_prefix:
                    if char.strip():
                        t = idx / max(1, total_chars - 1)
                        r, g, b = rgb_interp(start_color, end_color, t)
                        colored_before += f"\033[38;2;{r};{g};{b}m{char}\033[0m"
                        idx += 1
                    else:
                        colored_before += char
                
                white_prefix_colored = f"\033[38;2;255;255;255m{prefix_part}\033[0m"
                
                colored_word = ""
                word_chars = [char for char in word_part if char.strip()]
                for i, char in enumerate(word_part):
                    if char.strip():
                        t = i / max(1, len(word_chars) - 1)
                        r, g, b = rgb_interp(start_color, end_color, t)
                        colored_word += f"\033[38;2;{r};{g};{b}m{char}\033[0m"
                    else:
                        colored_word += char
                
                result_lines.append(colored_before + white_prefix_colored + colored_word + after_word)
            else:
                colored_line = ""
                total_chars = sum(1 for char in line if char.strip())
                idx = 0
                for char in line:
                    if char.strip():
                        t = idx / max(1, total_chars - 1)
                        r, g, b = rgb_interp(start_color, end_color, t)
                        colored_line += f"\033[38;2;{r};{g};{b}m{char}\033[0m"
                        idx += 1
                    else:
                        colored_line += char
                result_lines.append(colored_line)
        else:
            colored_line = ""
            total_chars = sum(1 for char in line if char.strip())
            idx = 0
            for char in line:
                if char.strip():
                    t = idx / max(1, total_chars - 1)
                    r, g, b = rgb_interp(start_color, end_color, t)
                    colored_line += f"\033[38;2;{r};{g};{b}m{char}\033[0m"
                    idx += 1
                else:
                    colored_line += char
            result_lines.append(colored_line)
    
    return "\n".join(result_lines)


_ascii_art = """
██╗   ██╗███████╗██╗      ██████╗ ██████╗  █████╗
██║   ██║██╔════╝██║     ██╔═══██╗██╔══██╗██╔══██╗
██║   ██║█████╗  ██║     ██║   ██║██████╔╝███████║
╚██╗ ██╔╝██╔══╝  ██║     ██║   ██║██╔══██╗██╔══██║
 ╚████╔╝ ███████╗███████╗╚██████╔╝██║  ██║██║  ██║
  ╚═══╝  ╚══════╝╚══════╝ ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝
                                    Made by neoarz
"""

# Info message about supported sites and README link
INFO_MESSAGE = """
Supports YouTube, TikTok, Instagram, and more!
See the full list of supported sites here: \033[34mhttps://github.com/yt-dlp/yt-dlp/blob/master/supportedsites.md\033[0m
"""

_start_rgb = (180, 0, 255)
_end_rgb = (0, 140, 255)  

ascii = gradient_text_selective(_ascii_art, _start_rgb, _end_rgb, "neoarz", "Made by ")

ascii_plain = _ascii_art