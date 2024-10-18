import pygame
import random
import os
import subprocess
import warnings
import time
warnings.filterwarnings("ignore")

# 初始化 pygame
pygame.init()
pygame.mixer.init()

lossless_dir = "lossless_files"  # 無損音檔資料夾
if not os.path.exists(lossless_dir):
    os.makedirs(lossless_dir)
    print(f"已建立資料夾: {lossless_dir}")
    print("請將無損音檔放入此資料夾後重新執行程式。")
    exit()  # 程式結束，等待使用者放入檔案

# 遞迴地列出所有子目錄中的檔案，並允許使用者逐層選擇
def list_files_recursive(directory):
    current_dir = os.path.abspath(directory)
    parent_dir = os.path.dirname(current_dir)

    while True:
        subdirs = [d for d in os.listdir(current_dir) 
                   if os.path.isdir(os.path.join(current_dir, d)) and not d.startswith(".")] # 忽略隱藏目錄
        files = [f for f in os.listdir(current_dir) 
                 if os.path.isfile(os.path.join(current_dir, f)) and not f.startswith(".")] # 忽略隱藏檔案

        if not subdirs and not files:
            print(f"資料夾 '{current_dir}' 中沒有任何（非隱藏）檔案或子目錄。")
            return []

        print(f"目前資料夾: {current_dir}")
        if subdirs:
            print("子目錄:")
            for i, subdir in enumerate(subdirs):
                print(f"{i+1}. {subdir}")
        if files:
            print("檔案:")
            for i, file in enumerate(files):
                print(f"{i+1+len(subdirs)}. {file}")
        if not subdirs and not files:
            choice = input("此資料夾無檔案及資料夾，請按Enter返回上一層")
            choice = 0

        choice = input("\n請選擇子目錄或檔案 (輸入數字, 0 返回上層): ")
        try:
            choice = int(choice)
            if choice == 0:
                if current_dir == directory:
                    print("已在最上層目錄。")
                elif current_dir == parent_dir and parent_dir != directory:
                    print("返回初始目錄")
                    current_dir = directory
                    parent_dir = os.path.dirname(current_dir)
                else:
                    current_dir = os.path.dirname(current_dir)

            elif 1 <= choice <= len(subdirs):
                current_dir = os.path.join(current_dir, subdirs[choice - 1])
            elif len(subdirs) < choice <= len(subdirs) + len(files):
                return [os.path.join(current_dir, files[choice - len(subdirs) - 1])]
            else:
                print("無效的選擇，請重新輸入。")
        except ValueError:
            print("無效的輸入，請輸入數字。")

# 列出所有無損音檔
lossless_file = list_files_recursive(lossless_dir)[0]

if not lossless_file:
    print("請放入無損音檔後重新執行程式。")
    exit()

# 輸入 MP3 位元率
bitrate = input("請輸入 MP3 位元率kbps (例如: 128, 192, 256, 320): ")

save_dir = "created_files"
if not os.path.exists(save_dir):
    os.makedirs(save_dir)

# MP3 輸出路徑，包含位元率資訊
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

# 音檔列表 (包含無損和轉換後的 MP3)
sound_files = [lossless_file, mp3_file]

# 隨機選擇 a 和 b 對應的音檔，確保 a 和 b 不同
a_file = random.choice(sound_files)
b_file = random.choice([f for f in sound_files if f != a_file])

# 起始播放 a
current_file = a_file

# 函數來播放指定音檔並從指定位置開始播放
def play_sound(sound_file, position=0):
    pygame.mixer.music.load(sound_file)
    pygame.mixer.music.play(start=position)
    print(f"\n\n現在在播放: {'a' if sound_file == a_file else 'b'}")
    # print(f"開始時間: {position:.2f} 秒")

# 檢查音檔播放狀態
def is_playing():
    return pygame.mixer.music.get_busy()

# 暫停/繼續播放
def toggle_pause():
    if pygame.mixer.music.get_busy():
        pygame.mixer.music.pause()
        global position
        curr = position + pygame.mixer.music.get_pos() / 1000  # 當前播放位置
        # print(f"暫停播放: {curr:.2f} 秒（按空白鍵繼續播放）")
    else:
        pygame.mixer.music.unpause()
        # print("繼續播放（按空白鍵暫停播放）")

# 快進/快退功能
def seek_sound(offset):
    global position
    curr = position + pygame.mixer.music.get_pos() / 1000  # 當前播放位置
    position = max(0, curr + offset)  # 確保位置不會小於 0
    pygame.mixer.music.play(start=position)
    # if offset > 0:
    #     print(f"+5s >> {curr:.2f} 秒")
    # else:
    #     print(f"-5s >> {curr:.2f} 秒")

# 程式主邏輯
print("按 'Enter' 切換音檔, 'q' 退出, '左鍵' -5s, '右鍵' +5s, '空白鍵' 暫停/繼續")

# 播放初始的 a 檔案
position = 0
play_sound(current_file)

running = True
last_update_time = time.time()

while running:
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:
                # 程式退出時印出 a 和 b 對應的檔名
                print(f"a 對應的檔名: {a_file}")
                print(f"b 對應的檔名: {b_file}")
                running = False
            elif event.key == pygame.K_RETURN:
                # 切換音檔並從相同的位置繼續播放
                position += pygame.mixer.music.get_pos() / 1000  # 將毫秒轉換為秒
                current_file = b_file if current_file == a_file else a_file
                play_sound(current_file, position)
            elif event.key == pygame.K_LEFT:
                # 快退 5 秒
                seek_sound(-5)
            elif event.key == pygame.K_RIGHT:
                # 快進 5 秒
                seek_sound(5)
            elif event.key == pygame.K_SPACE:
                # 暫停/繼續播放
                toggle_pause()

    # 每秒更新一次當前播放位置
    update_interval = 0.05  # 預設每秒更新一次
    current_time = time.time()
    if current_time - last_update_time >= update_interval:
        if is_playing():
            curr_position = position + pygame.mixer.music.get_pos() / 1000  # 當前播放位置
            print(f"目前播放位置: {curr_position:.2f} 秒", end='\r')
        last_update_time = current_time


pygame.quit()
