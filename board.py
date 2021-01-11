import pygame as p
import chessengine

WIDTH = 512
HEIGHT = 512
DIMENSIONS = 8
SQUARE_SIZE = HEIGHT // DIMENSIONS
MAX_FPS = 15
IMAGES = {}
POSSIBLE_PLAYERS = ["YOU", "MINIMAX"]
MENU_LOCATIONS = [(4, 3), (5.2, 3), (4, 5), (5.2, 5), (6.8, 6.8), (4.8, 1), (6, 1)]
MENU_LOCATION_TO_TEXT = {(4, 3): "YOU", (5.2, 3): "MINIMAX", (4, 5): "YOU", (5.2, 5): "MINIMAX", \
    (6.8, 6.8): "CONTINUE", (4.8, 1): "white", (6, 1): "black"}
TEXTS = ["choose a color: ", "player 1: ", "player 2: "]
COL_TO_CATEGORY = {6.8: "continue",5:"opponent" , 3:"player" , 1:"color" }

class Board():
    def __init__(self):
        self.screen = p.display.set_mode((WIDTH, HEIGHT))
        self.colors = [p.Color("white"), p.Color("dark Gray")]
        self.clock = p.time.Clock()
        self.screen.fill(p.Color("white"))
        self.menu_phase = True
        self.running = True
        self.gs = chessengine.GameState()
        self.valid_moves = self.gs.getValidMoves()
        self.sq_selected = ()
        self.player_clicks = []
        self.move_made = False
        self.animate = False
        self.game_over = False
        self.flip = False
        self.player_color = ""
        self.player = ""
        self.opponent = ""
        self.menu_buttons = generate_menu_buttons()
    

#------------------------------------Board functios ----------------------------------------------------
    
    def drawText(self, text):
        s = p.Surface((SQUARE_SIZE*6, SQUARE_SIZE*2))
        s.set_alpha(256)
        s.fill(p.Color("Red"))
        self.screen.blit(s, (SQUARE_SIZE, 3 * SQUARE_SIZE))
        font = p.font.SysFont("Helvitca", 40, True, False)
        text_object = font.render(text, 0, p.Color("black"))
        text_location = p.Rect(0, 0, WIDTH, HEIGHT).move(WIDTH/2 - text_object.get_width()/2, HEIGHT/2 - text_object.get_height()/2)
        self.screen.blit(text_object, text_location)

    def highlightSquares(self):
        if self.sq_selected != () and len(self.sq_selected) == 2:
            r, c = self.sq_selected
            color = 'w' if self.gs.white_to_move else 'b'
            if self.gs.board[r][c][0] == color:
                #highlight square pressed
                s = p.Surface((SQUARE_SIZE, SQUARE_SIZE))
                s.set_alpha(100)
                s.fill(p.Color("blue"))
                self.screen.blit(s, (c * SQUARE_SIZE, r * SQUARE_SIZE))
                #highlight valid moves
                s.fill(p.Color("yellow"))
                for move in self.valid_moves:
                    if move.start_row == r and move.start_col == c:
                        self.screen.blit(s, (move.end_col * SQUARE_SIZE, move.end_row * SQUARE_SIZE))

    def animateMove(self, move):
        row_diff = move.end_row - move.start_row
        col_diff = move.end_col - move.start_col
        frames_per_sq = 5
        frame_count = (abs(row_diff) + abs(col_diff)) * frames_per_sq
        for frame in range(frame_count + 1):
            r, c = (move.start_row + row_diff*frame/frame_count, move.start_col + col_diff*frame/frame_count)
            self.draw_board()
            self.draw_pieces()
            color = self.colors[(move.end_row + move.end_col) % 2]
            end_square = p.Rect(move.end_col * SQUARE_SIZE, move.end_row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
            p.draw.rect(self.screen, color, end_square)
            if move.piece_captured != "--":
                self.screen.blit(IMAGES[move.piece_captured], end_square)
            #draw moving piece
            self.screen.blit(IMAGES[move.piece_moved], p.Rect(c*SQUARE_SIZE, r*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
            p.display.flip()
            self.clock.tick(60)

    def draw_game_state(self):
        self.draw_board()
        self.highlightSquares()
        self.draw_pieces()

    def draw_board(self):
        for r in range (DIMENSIONS):
            for c in range (DIMENSIONS):
                color = self.colors[(r+c)%2]
                p.draw.rect(self.screen, color, p.Rect(c*SQUARE_SIZE, r*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

    def draw_pieces(self):
        for r in range (DIMENSIONS):
            for c in range (DIMENSIONS):
                piece = self.gs.board[r][c]
                if piece != "--":
                    self.screen.blit(IMAGES[piece], p.Rect(c*SQUARE_SIZE, r*SQUARE_SIZE, r*SQUARE_SIZE, c*SQUARE_SIZE))

    def getEvent(self, e):
        if e.type == p.QUIT:
            self.running = False
        elif e.type == p.MOUSEBUTTONDOWN:
            if not self.game_over:
                location = p.mouse.get_pos()
                col = location[0]//SQUARE_SIZE
                row = location[1]//SQUARE_SIZE
                if self.sq_selected == (row, col):
                    self.sq_selected = ()
                    self.player_clicks = []
                else:
                    self.sq_selected = (row, col)
                    self.player_clicks.append(self.sq_selected)
                if len(self.player_clicks) == 2:
                    move = chessengine.Move(self.player_clicks[0], self.player_clicks[1], self.gs.board)
                    for i in range(len(self.valid_moves)):
                        if move == self.valid_moves[i]:
                            self.gs.makeMove(self.valid_moves[i])
                            self.move_made = True
                            self.animate = True
                            self.sq_selected = ()
                            self.player_clicks = [] 
                    if not self.move_made:
                        self.player_clicks = [self.sq_selected]
        # keyself presses
        elif e.type == p.KEYDOWN:
            if e.key == p.K_z:
                self.gs.undoMove()
                self.move_made = True
                self.animate = False
                self.game_over = False
            if e.key == p.K_r:
                self.gs = chessengine.GameState()
                if self.flip:
                    self.gs.flipBoard()
                self.valid_moves = self.gs.getValidMoves()
                self.sq_selected = ()
                self.player_clicks = []
                self.move_made = False
                self.animate = False
                self.game_over = False

    def updateMenu(self, e):
        if e.type == p.QUIT:
            self.menu_phase = False
            self.player_color = "white"
            self.player = "YOU"
            self.opponent = "YOU"
        elif e.type == p.MOUSEBUTTONDOWN:
            click_location = p.mouse.get_pos()
            col = click_location[0]/SQUARE_SIZE
            row = click_location[1]/SQUARE_SIZE
            for button in self.menu_buttons:
                if button.location[0] <= col <= button.location[0] + 1 and button.location[1] <= row <= button.location[1] + 1:
                    if button.category == "color":
                        self.player_color = MENU_LOCATION_TO_TEXT[button.location]
                    elif button.category == "player":
                        self.player = MENU_LOCATION_TO_TEXT[button.location]
                    elif button.category == "opponent":
                        self.opponent = MENU_LOCATION_TO_TEXT[button.location]
                    elif button.category == "continue" and self.player != "" and self.opponent != "" and self.player_color != "":
                        self.menu_phase = False
                    for click in self.player_clicks:
                        if click[1] == button.location[1]:
                            self.player_clicks.remove(click)
                    self.player_clicks.append(button.location)
        self.clock.tick(MAX_FPS)
        p.display.flip()
        
    def drawMenu(self):
        p.draw.rect(self.screen, p.Color("dark gray"), p.Rect(0, 0, WIDTH, HEIGHT))
        s = p.Surface((SQUARE_SIZE, SQUARE_SIZE))
        s.set_alpha(200)
        font = p.font.SysFont("bahnschrift", 25, True, False)
        for i, text in enumerate(TEXTS):
            text_object = font.render(text, 0, p.Color("black"))
            text_location = p.Rect(0, 0, WIDTH, HEIGHT).move(WIDTH/8, HEIGHT/6 + 2*i*SQUARE_SIZE)
            self.screen.blit(text_object, text_location)
        for location in MENU_LOCATIONS:
            if location == (6, 1):
                s.fill(p.Color("black"))
            else:
                s.fill(p.Color("white"))
            self.screen.blit(s, (SQUARE_SIZE * location[0], SQUARE_SIZE * location[1]))
            font = p.font.SysFont("bahnschrift", 10, True, False)
            text_object = font.render(MENU_LOCATION_TO_TEXT[location], 0, p.Color("black")) if location != (6, 1)\
                 else font.render(MENU_LOCATION_TO_TEXT[location], 0, p.Color("white"))
            text_location = p.Rect(0, 0, SQUARE_SIZE, SQUARE_SIZE).move(SQUARE_SIZE * location[0] + \
                (SQUARE_SIZE - text_object.get_width())/2, SQUARE_SIZE * location[1] + (SQUARE_SIZE - text_object.get_height())/2)
            self.screen.blit(text_object, text_location)
        for click in self.player_clicks:
            changeSquareColor(self.screen, click)


#---------------------------------------------------------------------------------------------------------------------
        
def playGame():
    board = Board()
    load_images()
    while board.menu_phase:
        board.drawMenu()
        for e in p.event.get():
            board.updateMenu(e)
        board.clock.tick(MAX_FPS)
        p.display.flip()
    if board.player_color == "black":
        board.gs.flipBoard()
        board.flip = True
    board.player_clicks = []
    board.valid_moves = board.gs.getValidMoves()
    while board.running:
        # if it's the oponent's turn use minimax to make the next move
        if board.gs.white_to_move and board.player_color == "white" and board.player == "MINIMAX"\
            or board.gs.white_to_move and board.player_color != "white" and board.opponent == "MINIMAX"\
            or not board.gs.white_to_move and board.player_color != "white" and board.player == "MINIMAX"\
            or not board.gs.white_to_move and board.player_color == "white" and board.opponent == "MINIMAX":
            if not board.game_over:    
                best_move = board.gs.getBestMove(3)
                board.gs.makeMove(best_move)
                board.move_made = True
                board.animate = True
        else:
            for e in p.event.get():
                board.getEvent(e)   
        if board.move_made:
            if board.animate:
                board.animateMove(board.gs.move_log[len(board.gs.move_log) - 1])
            board.valid_moves = board.gs.getValidMoves()
            board.move_made = False
            board.animate = False

        board.draw_game_state()
        if board.gs.check_mate:
            board.game_over = True
            if board.gs.white_to_move:
                board.drawText("BLACK WON THE GAME")
            else:
                board.drawText("WHITE WON THE GAME")
        if board.gs.stale_mate:
            board.game_over = True
            board.drawText("IT'S A DRAW")
        board.clock.tick(MAX_FPS)
        p.display.flip()


def changeSquareColor(screen, location):
    s = p.Surface((SQUARE_SIZE, SQUARE_SIZE))
    s.set_alpha(80)
    s.fill(p.Color("green"))
    screen.blit(s, (SQUARE_SIZE * location[0], SQUARE_SIZE * location[1]))

def load_images():
    pieces = ['wp', 'wR', 'wN', 'wB', 'wK', 'wQ', 'bp', 'bR', 'bN', 'bB', 'bK', 'bQ']
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load("images/" + piece +".png"), (SQUARE_SIZE, SQUARE_SIZE))

#--------------------------------------Button functions------------------------------------------------

class Button():
    def __init__(self, location):
        self.location = location
        self.text = MENU_LOCATION_TO_TEXT[location]
        self.category = COL_TO_CATEGORY[location[1]]
    
    
def generate_menu_buttons():
    menu_buttons = []
    for location in MENU_LOCATIONS:
        temp_button = Button(location)
        menu_buttons.append(temp_button)
    return menu_buttons

