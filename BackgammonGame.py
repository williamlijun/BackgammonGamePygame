import pygame
import os
import random
import tkinter as tk
from tkinter import messagebox

# 初始化 Pygame
pygame.init()

# 设置窗口大小、标题、背景音乐
screen = pygame.display.set_mode((424, 424))
pygame.display.set_caption("五子棋")
background_music_path = "background_music.mp3"
if os.path.exists(background_music_path):
    pygame.mixer.music.load(background_music_path)
    pygame.mixer.music.play(-1)

# 载入棋盘图片
board_image = pygame.image.load("checkerboard.png")  # 424*424
board_image = pygame.transform.scale(board_image, (424, 424))

# 棋盘设置
GRID_SIZE = 26.5  # 424//16 单个格子大小
BOARD_SIZE = 16  # 14*14 另去掉4个边框
board = [[0 for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]  # 16*16

# 棋子颜色定义
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# 棋子状态
current_player = 1  # 1表示黑子，-1表示白子

# 游戏状态
game_over = False

# 记录比分
human_score = 0
ai_score = 0


# 渲染棋盘和落子
def draw_board():
    screen.blit(board_image, (0, 0))
    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            if board[r][c] == 1:
                pygame.draw.circle(screen, BLACK, (c * GRID_SIZE, r * GRID_SIZE), 12)
            elif board[r][c] == -1:
                pygame.draw.circle(screen, WHITE, (c * GRID_SIZE, r * GRID_SIZE), 12)


# 检测是否有人获胜（有五子连线）
def check_winner(row, col):
    player = board[row][col]
    directions = [
        (0, 1),  # 水平方向
        (1, 0),  # 垂直方向
        (1, 1),  # 左上到右下的斜线
        (1, -1)  # 右上到左下的斜线
    ]

    for delta_row, delta_col in directions:
        count = 1  # 当前点也算一个棋子
        # 检查当前棋子是否五子连线
        # 累计正向棋子数量
        for i in range(1, 5):
            r = row + delta_row * i
            c = col + delta_col * i
            if r < 1 or r >= BOARD_SIZE - 1 or c < 1 or c >= BOARD_SIZE - 1 or board[r][c] != player:  # 越界与非当前棋子检查
                break
            count += 1
        # 累计反向棋子数量
        for i in range(1, 5):
            r = row - delta_row * i
            c = col - delta_col * i
            if r < 1 or r >= BOARD_SIZE - 1 or c < 1 or c >= BOARD_SIZE - 1 or board[r][c] != player:
                break
            count += 1

        if count >= 5:
            return True

    return False


# 重新开始游戏
def reset_game():
    global board, game_over, current_player
    board = [[0 for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
    game_over = False
    current_player = 1


# 显示战况对话框
def show_game_status():
    global human_score, ai_score
    root.withdraw()  # 隐藏主窗口
    status = f"当前比分\n\n人类玩家：{human_score}\nAI：{ai_score}"
    messagebox.showinfo("战况", status)
    root.deiconify()  # 重新显示主窗口


# 游戏结束后显示结果
def show_winner_dialog(winner):
    global human_score, ai_score
    if winner == 1:
        human_score += 1
        messagebox.showinfo("游戏结束", "黑棋获胜！")
    elif winner == -1:
        ai_score += 1
        messagebox.showinfo("游戏结束", "白棋获胜！")
    reset_game()  # 重新开始游戏


# ai 落子
# 评估函数
def evaluate_position(row, col, player):
    """评估当前棋盘位置的分数，越高表示该位置越有利。"""
    score = 0
    opponent = 1 if player == -1 else -1  # 确定对手的玩家

    for delta_row, delta_col in [
        (0, 1), (1, 0), (1, 1), (1, -1)
    ]:
        count = 1  # 当前棋子
        ends_open = [False, False]  # 检查两端是否开放

        # 正向检查
        for i in range(1, 5):
            r, c = row + delta_row * i, col + delta_col * i
            if 1 <= r < BOARD_SIZE-1 and 1 <= c < BOARD_SIZE-1:
                if board[r][c] == player:
                    count += 1
                elif board[r][c] == opponent:
                    break
                else:  # 空位
                    ends_open[0] = True  # 标记正向有空位
                    break
            else:
                break

        # 反向检查
        for i in range(1, 5):
            r, c = row - delta_row * i, col - delta_col * i
            if 1 <= r < BOARD_SIZE-1 and 1 <= c < BOARD_SIZE-1:
                if board[r][c] == player:
                    count += 1
                elif board[r][c] == opponent:
                    break
                else:  # 空位
                    ends_open[1] = True  # 标记反向有空位
                    break
            else:
                break

        # 根据连线的数量和相邻情况增加分数
        if count >= 5:
            return 10000  # 赢得比赛
        elif count == 4:
            if ends_open[0] and ends_open[1]:
                score += 8000  # 四连且两端空位
            else:
                score += 5000  # 普通四连
        elif count == 3:
            if ends_open[0] and ends_open[1]:
                score += 3000  # 三连且两端空位
            elif ends_open[0] or ends_open[1]:
                score += 2000  # 一端有空位的三连
            else:
                score += 1000  # 普通三连

    return score


def find_best_random_position():
    # 优先考虑中心位置及其周围的位置
    center_positions = [
        (BOARD_SIZE // 2, BOARD_SIZE // 2),
        (BOARD_SIZE // 2 - 1, BOARD_SIZE // 2),
        (BOARD_SIZE // 2, BOARD_SIZE // 2 - 1),
        (BOARD_SIZE // 2 - 1, BOARD_SIZE // 2 - 1),
        (BOARD_SIZE // 2 + 1, BOARD_SIZE // 2),
        (BOARD_SIZE // 2, BOARD_SIZE // 2 + 1),
        (BOARD_SIZE // 2 + 1, BOARD_SIZE // 2 + 1),
        (BOARD_SIZE // 2 - 1, BOARD_SIZE // 2 + 1),
        (BOARD_SIZE // 2 + 1, BOARD_SIZE // 2 - 1)
    ]

    # 首先检查中心位置及其周围
    for pos in center_positions:
        r, c = pos
        if 1 <= r < BOARD_SIZE-1 and 1 <= c < BOARD_SIZE-1 and board[r][c] == 0:
            return r, c

    # 如果中心附近没有空位，随机选择其他空位
    empty_positions = [(r, c) for r in range(1, BOARD_SIZE - 1) for c in range(1, BOARD_SIZE - 1) if board[r][c] == 0]

    if empty_positions:
        return random.choice(empty_positions)

    return None  # 如果棋盘已满，返回None


def ai_move():
    best_score = -float('inf')
    human_best_score = -float('inf')
    best_position_1 = None
    best_position_2 = None

    # 优先检测阻止对手获胜，采用评估函数
    for r in range(1, BOARD_SIZE - 1):
        for c in range(1, BOARD_SIZE - 1):
            if board[r][c] == 0:
                board[r][c] = 1  # 人类落子
                human_score = evaluate_position(r, c, 1)
                board[r][c] = 0
                # 更新人类最佳得分和位置
                if human_score > human_best_score:
                    human_best_score = human_score
                    best_position_1 = (r, c)
    # 如果人类当前3子连珠，马上阻止
    if human_best_score >= 1000:
        print(human_best_score)
        return best_position_1

    # 评估AI的最佳落子位置
    for r in range(1, BOARD_SIZE - 1):
        for c in range(1, BOARD_SIZE - 1):
            if board[r][c] == 0:
                board[r][c] = -1  # AI落子
                score = evaluate_position(r, c, -1)
                board[r][c] = 0  # 撤回落子
                # 更新最佳得分和位置
                if score > best_score:
                    best_score = score
                    best_position_2 = (r, c)
    # 确保始终返回一个最佳落子
    if best_score > human_best_score and best_position_2 is not None and best_score > 0:
        return best_position_2
    elif best_position_1 is not None and human_best_score > 0:
        return best_position_1

    # 如果没有找到位置，使用优化后的随机选择
    empty_position = find_best_random_position()
    if empty_position is not None:
        return empty_position

    return None  # 如果棋盘已满，返回None


def on_close():
    pygame.quit()  # 退出 Pygame
    root.destroy()  # 关闭 Tkinter 窗口


# 创建菜单栏
root = tk.Tk()  # 将 root 设为全局变量
root.title("菜单")
menu_bar = tk.Menu(root)

# 创建战况菜单
status_menu = tk.Menu(menu_bar, tearoff=0)
status_menu.add_command(label="查看当前战况", command=show_game_status)
status_menu.add_command(label="重新开始游戏", command=reset_game)
status_menu.add_command(label="退出游戏", command=on_close)  # 退出按钮
menu_bar.add_cascade(label="选项", menu=status_menu)

root.config(menu=menu_bar)

root.protocol("WM_DELETE_WINDOW", on_close)  # 处理关闭事件
root.withdraw()  # 先隐藏窗口

# 显示菜单
root.deiconify()  # 显示菜单

# 主游戏循环
running = True
while running:
    for event in pygame.event.get():
        # 获取游戏运行事件
        if event.type == pygame.QUIT:
            running = False
            on_close()  # 关闭菜单
        # 获取鼠标点击事件
        elif event.type == pygame.MOUSEBUTTONDOWN and not game_over:
            # 获取点击坐标
            y, x = event.pos
            row = round(x / GRID_SIZE)
            col = round(y / GRID_SIZE)

            if 1 <= row < BOARD_SIZE and 1 <= col < BOARD_SIZE and board[row][col] == 0:  # 越界和棋子状态判断
                # 人类（黑棋）先落子
                current_player = 1
                board[row][col] = current_player
                if check_winner(row, col):
                    game_over = True
                    show_winner_dialog(current_player)
                else:
                    # ai落子
                    current_player = -1
                    ai_move_position = ai_move()
                    if ai_move_position:
                        r, c = ai_move_position
                        board[r][c] = -1
                        if check_winner(r, c):
                            game_over = True
                            show_winner_dialog(current_player)
    # 重新渲染棋盘
    draw_board()
    pygame.display.flip()

    # 更新 Tkinter 窗口
    root.update()

pygame.quit()
