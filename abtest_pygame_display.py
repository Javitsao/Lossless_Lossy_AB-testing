import pygame
import random
import os
import subprocess
import requests
import librosa
import numpy as np

# 定義下載字體的函數
def download_font(font_url, save_path):
    response = requests.get(font_url)
    if response.status_code == 200:
        with open(save_path, 'wb') as f:
            f.write(response.content)
        print(f"字體下載成功並儲存到: {save_path}")
    else:
        print(f"下載字體失敗，狀態碼: {response.status_code}")
        exit()

# 字體下載 URL 和儲存路徑
font_url = "https://github.com/googlefonts/noto-cjk/raw/main/Sans/OTF/TraditionalChinese/NotoSansCJKtc-Regular.otf"
font_path = "NotoSansCJKtc-Regular.otf"

# 如果字體不存在，下載字體
if not os.path.exists(font_path):
    print("字體文件不存在，正在下載...")
    download_font(font_url, font_path)

# 初始化 pygame
pygame.init()
pygame.mixer.init()

# 定義視窗大小
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("音樂播放器")

# 載入下載的字體
font = pygame.font.Font(font_path, 20)

# 顏色定義 (新增背景顏色)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (60, 60, 220)
LIGHT_BLUE = (173, 216, 230)
LIGHT_PURPLE = (255, 0, 255)
GRAY = (128, 128, 128)
ORANGE = (255, 165, 0)
LIGHT_PINK = (255, 182, 193)
BACKGROUND = (25, 25, 25)  # 設定背景顏色為黑色
TEXT_COLOR = (255, 255, 255)  # 設定文字顏色為白色


lossless_dir = "lossless_files"  # 無損音檔資料夾
if not os.path.exists(lossless_dir):
    os.makedirs(lossless_dir)
    print(f"已建立資料夾: {lossless_dir}")
    print("請將無損音檔放入此資料夾後重新執行程式。")
    exit()

# 遞迴列出資料夾及檔案，排除隱藏檔案
def list_files_recursive(directory):
    files_and_dirs = []
    for entry in os.scandir(directory):
        if not entry.name.startswith('.') and (entry.is_file() or entry.is_dir()):
            files_and_dirs.append(entry.path)
    return files_and_dirs

# 檔案瀏覽功能，顯示資料夾及檔案 (修改背景顏色和選中顏色)
def file_selection_screen(start_dir):
    current_dir = start_dir
    selected_index = 0
    scroll_offset = 0
    max_display = 10  # 一次顯示的最大行數

    while True:
        # 列出當前資料夾下的所有檔案和資料夾
        files_and_dirs = list_files_recursive(current_dir)

        # 處理滾動條
        visible_files = files_and_dirs[scroll_offset:scroll_offset + max_display]

        screen.fill(BACKGROUND)  # 使用 BACKGROUND 顏色填充背景
        draw_text(f"當前目錄: {os.path.basename(current_dir)}", 50, 20, LIGHT_PURPLE)
        draw_text("選擇音檔 (上下鍵選擇，Enter確定，Backspace上一層)", 50, 50, LIGHT_PURPLE)

        for i, item in enumerate(visible_files):
            if i + scroll_offset == selected_index:
                # 塗滿藍色矩形
                pygame.draw.rect(screen, BLUE, (50, 101 + i * 30, 710, 30))
                color = WHITE  # 選中項目的文字顏色為白色
            else:
                color = TEXT_COLOR  # 非選中項目的文字顏色

            display_name = os.path.basename(item) + ('/' if os.path.isdir(item) else '')
            draw_text(display_name, 50, 100 + i * 30, color)

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP and selected_index > 0:
                    selected_index -= 1
                    if selected_index < scroll_offset:
                        scroll_offset -= 1
                elif event.key == pygame.K_DOWN and selected_index < len(files_and_dirs) - 1:
                    selected_index += 1
                    if selected_index >= scroll_offset + max_display:
                        scroll_offset += 1
                elif event.key == pygame.K_RETURN:
                    selected_item = files_and_dirs[selected_index]
                    if os.path.isdir(selected_item):
                        current_dir = selected_item  # 進入資料夾
                        selected_index, scroll_offset = 0, 0
                    else:
                        return selected_item  # 返回選擇的檔案
                elif event.key == pygame.K_BACKSPACE and current_dir != start_dir:
                    current_dir = os.path.dirname(current_dir)  # 回到上一層目錄
                    selected_index, scroll_offset = 0, 0

# 繪製文字到 pygame 視窗 (使用 TEXT_COLOR)
def draw_text(text, x, y, color=TEXT_COLOR): # 使用 TEXT_COLOR 作為預設顏色
    text_surface = font.render(text, True, color)
    screen.blit(text_surface, (x, y))


# 呼叫檔案選擇畫面
lossless_file = file_selection_screen(lossless_dir)

# 輸入 MP3 位元率
bitrate = ""
input_mode = True
while input_mode:
    screen.fill(BACKGROUND) # 背景顏色
    draw_text("請輸入 MP3 位元率 (例如: 128, 192, 256, 320)", 50, 50, LIGHT_PURPLE)
    draw_text("kbps", 200, 150, LIGHT_PURPLE)
    pygame.draw.rect(screen, GRAY, (59, 151.5, 100, 30))  # 塗滿灰色矩形
    draw_text(bitrate, 89, 150, GREEN)  # 文字顏色
    pygame.display.update()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                input_mode = False
            elif event.key == pygame.K_BACKSPACE:
                bitrate = bitrate[:-1]
            else:
                bitrate += event.unicode

save_dir = "created_files"
if not os.path.exists(save_dir):
    os.makedirs(save_dir)

mp3_file = os.path.join(save_dir, f"{os.path.splitext(os.path.basename(lossless_file))[0]}_{bitrate}.mp3")


# 使用 ffmpeg 轉換成指定位元率的 MP3 (如果檔案不存在)
if not os.path.exists(mp3_file):
    command = [
        'ffmpeg', '-i', lossless_file, '-ab', f'{bitrate}k', '-vn', '-map_metadata', '-1', mp3_file
    ]
    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        print(f"ffmpeg 轉換失敗: {e}")
        exit(1)


sound_files = [lossless_file, mp3_file]

# 隨機選擇 a 和 b 對應的音檔，確保 a 和 b 不同
a_file = random.choice(sound_files)
b_file = random.choice([f for f in sound_files if f != a_file])

current_file = a_file

# 函數來播放指定音檔，並在播放結束時顯示檔案名稱
def play_sound(sound_file, position=0):
    pygame.mixer.music.load(sound_file)
    pygame.mixer.music.play(start=position)


    # 設定播放結束事件
    pygame.mixer.music.set_endevent(pygame.USEREVENT + 1)


# 預先計算音頻數據 (修正：只計算振幅)
y, sr = librosa.load(current_file)
hop_length = 512  # 跳躍長度，控制頻譜的時間解析度
frequencies, amplitudes = librosa.magphase(librosa.stft(y, hop_length=hop_length))  # 計算頻率和振幅

# 主迴圈，用來處理鍵盤輸入和畫面更新
running = True
is_paused = False
update_interval = 0  # 更新間距，單位為毫秒
last_update_time = pygame.time.get_ticks()

# 初始化柱狀圖高度
bar_heights = [0] * 150

# 程式主邏輯
position = 0
current_time = 0
play_sound(current_file)

while running:
    screen.fill(BACKGROUND)
    draw_text(f"正在播放: {'a' if current_file == a_file else 'b'}", 50, 50, GREEN)
    draw_text("Enter", 50, 100, ORANGE), draw_text("切換音檔", 200, 100, LIGHT_BLUE)
    draw_text("空白鍵", 50, 130, ORANGE), draw_text("暫停/繼續", 200, 130, LIGHT_BLUE)
    draw_text("左鍵", 50, 160, ORANGE), draw_text("-5s", 200, 160, LIGHT_BLUE)
    draw_text("右鍵", 50, 190, ORANGE), draw_text("+5s", 200, 190, LIGHT_BLUE)
    draw_text("q", 50, 220, ORANGE), draw_text("退出並顯示答案", 200, 220, LIGHT_BLUE)

    # 顯示播放進度時間
    if pygame.mixer.music.get_busy() or is_paused:
        current_time = round(position + pygame.mixer.music.get_pos() / 1000)
        minutes = current_time // 60
        seconds = current_time % 60
        draw_text(f"播放時間: {minutes:02}:{seconds:02}", 50, 350, LIGHT_PINK)
        # 音頻特效
        current_time = pygame.time.get_ticks()
        if current_time - last_update_time > update_interval:  # 控制更新頻率
            last_update_time = current_time

            current_position = pygame.mixer.music.get_pos() / 1000  # 取得當前播放位置 (秒)
            frame = int(current_position * sr / hop_length)  # 計算對應的頻譜幀

            # 繪製柱狀圖
            num_bars = 150  # 增加柱狀圖數量
            bar_width = 2  # 減少柱狀圖寬度
            bar_spacing = 1  # 減少柱狀圖間距
            total_bar_width = num_bars * (bar_width + bar_spacing)
            x_offset = (WIDTH - total_bar_width) // 2  # 計算 x 偏移量

            for i in range(num_bars):
                # 將頻率映射到柱狀圖索引
                if frame < amplitudes.shape[1]:  # 檢查 frame 是否超出範圍
                    freq_index = int(i * len(frequencies) / num_bars)
                    
                    # 根據振幅調整 bar 的增長幅度，振幅越大 bar 高度增長越多
                    amplitude = np.mean(amplitudes[freq_index, frame])
                    if amplitude > 0.95:  # 可以設定一個閾值，避免背景音也影響太多
                        growth_factor = amplitude * 300  # 
                    elif amplitude > 0.9:
                        growth_factor = amplitude * 200
                    elif amplitude > 0.8:
                        growth_factor = amplitude * 150
                    elif amplitude > 0.7:
                        growth_factor = amplitude * 100
                    else:
                        growth_factor = amplitude * 20  # 低於閾值時增長少一點
                    
                    new_bar_height = int(growth_factor)  # 使用增長因子計算 bar 高度
                    bar_heights[i] = int(bar_heights[i] * 0.98 + new_bar_height * 0.02)  # 平滑過渡

                    bar_x = x_offset + i * (bar_width + bar_spacing) + 80
                    bar_y = (HEIGHT // 2) - (bar_heights[i] // 2) + 60  # 固定在每個 bar 的中間，下移 80
                    bar_rect = pygame.Rect(bar_x, bar_y, bar_width, bar_heights[i])  # 使用平滑後的 bar_heights
                    pygame.draw.rect(screen, BLUE, bar_rect)

    pygame.display.update()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:
                running = False
            elif event.key == pygame.K_RETURN:
                position += pygame.mixer.music.get_pos() / 1000
                current_file = b_file if current_file == a_file else a_file
                play_sound(current_file, position)
            elif event.key == pygame.K_LEFT:
                position += pygame.mixer.music.get_pos() / 1000
                position = max(0, position - 5)
                play_sound(current_file, position)
            elif event.key == pygame.K_RIGHT:
                position += pygame.mixer.music.get_pos() / 1000
                position = position + 5
                play_sound(current_file, position)
            elif event.key == pygame.K_SPACE:
                if pygame.mixer.music.get_busy():
                    pygame.mixer.music.pause()
                    is_paused = True
                else:
                    pygame.mixer.music.unpause()
                    is_paused = False

        # 檢查音樂播放結束事件
        elif event.type == pygame.USEREVENT + 1:
            running = False

if not running:
    pygame.mixer.music.pause()
    is_paused = True

    # 倒數計時並允許按鍵退出
    for i in range(5, -1, -1):
        screen.fill(BACKGROUND)  # 每次迴圈都清除畫面，使用 BACKGROUND 顏色

        # 顯示檔案名稱和勾勾，使用 GREEN 顏色
        draw_text(f"a: {os.path.basename(a_file)}", 50, 50, GREEN if a_file == lossless_file else TEXT_COLOR)
        draw_text(f"{'✓' if a_file == lossless_file else ''}", 500, 50, GREEN if a_file == lossless_file else TEXT_COLOR)
        draw_text(f"b: {os.path.basename(b_file)}", 50, 100, GREEN if b_file == lossless_file else TEXT_COLOR)
        draw_text(f"{'✓' if b_file == lossless_file else ''}", 500, 100, GREEN if b_file == lossless_file else TEXT_COLOR)
        draw_text(f"程式將在 {i} 秒後退出，或按任意鍵退出", 50, 500, LIGHT_BLUE)  # 使用 TEXT_COLOR
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                pygame.quit()
                exit()
        pygame.time.delay(1000)

pygame.quit()