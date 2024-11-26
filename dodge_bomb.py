import os
import random
import sys
import time

import pygame as pg


WIDTH, HEIGHT = 1100, 650
DELTA = {
    pg.K_UP: (0, -5),
    pg.K_DOWN: (0, +5),
    pg.K_LEFT: (-5, 0),
    pg.K_RIGHT: (+5, 0),
}
os.chdir(os.path.dirname(os.path.abspath(__file__)))


def check_bound(rct: pg.Rect) -> tuple[bool, bool]:
    """
    引数で与えられたRectが画面の中か外かを判定する
    引数：こうかとんRect or 爆弾Rect
    戻り値：真理値タプル（横，縦）／画面内：True，画面外：False
    """
    yoko, tate = True, True
    if rct.left < 0 or WIDTH < rct.right:
        yoko = False
    if rct.top < 0 or HEIGHT < rct.bottom:
        tate = False
    return yoko, tate


def get_kk_img(sum_mv: tuple[int, int]) -> pg.Surface:
    """
    移動量の合計値タプルに対応する向きの画像Surfaceを返す
    引数：移動量の合計値タプル
    戻り値：移動量の合計値タプルに対応する向きのこうかとん画像Surface
    """
    kk_left_img = pg.image.load("fig/3.png") 
    kk_right_img = pg.transform.flip(kk_left_img, True, False) 
    angle = 0
    
    if sum_mv[0] == -5:  # 左向きこうかとんを使用する
        img = kk_left_img
        if sum_mv == (-5, +5):  # 左下
            angle = 45
        elif sum_mv == (-5, 0):  # 左
            angle = 0
        elif sum_mv == (-5, -5):  # 左上
            angle = -45
    else:  # 右向きこうかとんを使用する
        img = kk_right_img
        if sum_mv == (0, -5):  # 上
            angle = 90
        elif sum_mv == (+5, -5):  # 右上
            angle = 45
        elif sum_mv == (+5, 0):  # 右
            angle = 0
        elif sum_mv == (+5, +5):  # 右下
            angle = -45
        elif sum_mv == (0, +5):  # 下
            angle = -90
    return pg.transform.rotozoom(img, angle, 0.9)


def init_bb_imgs() -> tuple[list[pg.Surface], list[int]]:
    """
    サイズの異なる爆弾Surfaceを要素としたリストと加速度リストを生成する
    引数：なし
    戻り値：爆弾のサイズごとのSurfaceリスト,各段階の加速度リストのタプル
    """
    bb_imgs = []  # 爆弾Surfaceリスト
    bb_accs = [a for a in range(1, 11)]  # 加速度リスト（1～10）
    for r in range(1, 11):  # 爆弾のサイズを10段階で生成
        bb_img = pg.Surface((20 * r, 20 * r))
        pg.draw.circle(bb_img, (255, 0, 0), (10 * r, 10 * r), 10 * r)
        bb_img.set_colorkey((0, 0, 0))  # 四隅の黒を透過させる
        bb_imgs.append(bb_img)  # リストに追加
    return bb_imgs, bb_accs


def gameover(screen: pg.Surface) -> None:
    """
    ゲームオーバー時に，半透明の黒い画面上に「Game Over」と表示する
    泣いているこうかとん画像を貼り付ける
    この状態を5秒間表示させる
    引数：Surface
    """
    # 半透明の黒い画面を描画
    overlay = pg.Surface((WIDTH, HEIGHT))  # 画面サイズのSurfaceを作成する
    overlay.fill((0, 0, 0))  # 黒で塗りつぶす
    overlay.set_alpha(200)  # 半透明を200に設定する
    screen.blit(overlay, (0, 0))

    # 「Game Over」のテキストの表示
    font_go = pg.font.Font(None, 80)  # フォントサイズは80
    text = font_go.render("Game Over", True, (255, 255, 255))  
    text_rct = text.get_rect()
    text_rct.center=(WIDTH/2, HEIGHT/2)  # 中央に配置
    screen.blit(text, text_rct)

    kc_img = pg.image.load("fig/8.png")  # 泣いているこうかとん画像を読み込む
    kc_rct = kc_img.get_rect()  
    kc_rct.center= WIDTH / 2 - 250, HEIGHT / 2
    screen.blit(kc_img, kc_rct)
    kc_rct.center= WIDTH/2 + 250, HEIGHT / 2
    screen.blit(kc_img, kc_rct)
        
    pg.display.update()
    time.sleep(5)  # 5秒間表示させる


def main():
    pg.display.set_caption("逃げろ！こうかとん")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    bg_img = pg.image.load("fig/pg_bg.jpg")    
    kk_img = pg.transform.rotozoom(pg.image.load("fig/3.png"), 0, 0.9)
    kk_rct = kk_img.get_rect()
    kk_rct.center = 300, 200
    bb_img = pg.Surface((20, 20))  # 爆弾用の空Surface
    pg.draw.circle(bb_img, (255, 0, 0), (10, 10), 10)  # 爆弾円を描く
    bb_img.set_colorkey((0, 0, 0))  # 四隅の黒を透過させる  
    bb_rct = bb_img.get_rect()  # 爆弾Rectの抽出
    bb_rct.centerx = random.randint(0, WIDTH)
    bb_rct.centery = random.randint(0, HEIGHT)
    vx, vy = +5, +5  # 爆弾速度ベクトル
    clock = pg.time.Clock()
    tmr = 0
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT: 
                return
        if kk_rct.colliderect(bb_rct):
            gameover(screen)
            return
        screen.blit(bg_img, [0, 0]) 

        key_lst = pg.key.get_pressed()
        sum_mv = [0, 0]
        for key, tpl in DELTA.items():
            if key_lst[key] == True:
                sum_mv[0] += tpl[0]
                sum_mv[1] += tpl[1]
        kk_img = get_kk_img(tuple(sum_mv))
        kk_rct.move_ip(sum_mv)
        # こうかとんが画面外なら，元の場所に戻す
        if check_bound(kk_rct) != (True, True):
            kk_rct.move_ip(-sum_mv[0], -sum_mv[1])
        screen.blit(kk_img, kk_rct)

        bb_imgs, bb_accs = init_bb_imgs()  # 爆弾の加速と拡大
        avx = vx*bb_accs[min(tmr//500, 9)]
        avy = vy*bb_accs[min(tmr//500, 9)]
        bb_img = bb_imgs[min(tmr//500, 9)]

        bb_rct.move_ip(avx, avy)  # 爆弾動く      
        yoko, tate = check_bound(bb_rct)
        if not yoko:  # 横にはみ出てる
            vx *= -1
        if not tate:  # 縦にはみ出てる
            vy *= -1
        screen.blit(bb_img, bb_rct)
        pg.display.update()
        tmr += 1
        clock.tick(50)


if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()