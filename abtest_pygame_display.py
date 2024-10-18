import pygame
import random
import os
import subprocess
import requests

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
font = pygame.font.Font(font_path, 24)

# 顏色定義
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

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

# 檔案瀏覽功能，顯示資料夾及檔案
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

        screen.fill(WHITE)
        draw_text(f"當前目錄: {os.path.basename(current_dir)}", 50, 20, RED)
        draw_text("選擇音檔 (上下鍵選擇，Enter確定，Backspace上一層)", 50, 50, RED)

        for i, item in enumerate(visible_files):
            color = RED if i + scroll_offset == selected_index else BLACK
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


# 繪製文字到 pygame 視窗
def draw_text(text, x, y, color=BLACK):
    text_surface = font.render(text, True, color)
    screen.blit(text_surface, (x, y))

# 呼叫檔案選擇畫面
lossless_file = file_selection_screen(lossless_dir)

# 輸入 MP3 位元率
bitrate = ""
input_mode = True
while input_mode:
    screen.fill(WHITE)
    draw_text("請輸入 MP3 位元率 (例如: 128, 192, 256, 320)", 50, 50, RED)
    draw_text(bitrate, 50, 150, BLACK)
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
    # print(f"現在在播放: {'a' if sound_file == a_file else 'b'}")

    # 設定播放結束事件
    pygame.mixer.music.set_endevent(pygame.USEREVENT + 1)


# 程式主邏輯
position = 0
current_time = 0
play_sound(current_file)

# 主迴圈，用來處理鍵盤輸入和畫面更新
running = True
is_paused = False
while running:
    screen.fill(WHITE)
    draw_text(f"正在播放: {'a' if current_file == a_file else 'b'}", 50, 50, BLACK)
    draw_text(f"按 'Enter' 切換音檔, 'q' 退出, '左鍵' -5s, '右鍵' +5s, '空白鍵' 暫停/繼續", 50, 100, BLACK)

    # 顯示播放進度時間
    if pygame.mixer.music.get_busy() or is_paused:
        current_time = round(position + pygame.mixer.music.get_pos() / 1000)
        minutes = current_time // 60
        seconds = current_time % 60
        draw_text(f"播放時間: {minutes:02}:{seconds:02}", 50, 150, BLACK)

    pygame.display.update()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:
                running = False
                pygame.mixer.music.pause()
                is_paused = True
                print("音樂播放結束") #  印出音樂播放結束訊息，與音樂播完時相同
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
            print("音樂播放結束") #  印出音樂播放結束訊息
            running = False


    if not running:
        screen.fill(WHITE)
        draw_text(f"檔案 a: {os.path.basename(a_file)}", 50, 50, BLACK)
        draw_text(f"檔案 b: {os.path.basename(b_file)}", 50, 100, BLACK)
        for i in range(5, 0, -1):
            screen.fill(WHITE)
            draw_text(f"程式將在 {i} 秒後退出", 50, 150, BLACK)
            pygame.display.update()
            pygame.time.delay(1000)
        pygame.display.update()
        pygame.time.delay(5000)
        pygame.quit()

pygame.quit()