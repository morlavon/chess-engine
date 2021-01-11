'''
the GameState class:
'''

class GameState():
    def __init__(self):
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]
        ]
        self.white_to_move = True
        self.flip = False
        self.move_log = []
        self.white_king_location = (7, 4)
        self.black_king_location = (0, 4)
        self.position = 0
        self.check_mate = False
        self.stale_mate = False
        self.enpassant_square = ()
        self.castling_rights = CastleRights(True, True, True, True)
        self.castling_rights_log = [CastleRights(True, True, True, True)]
        self.castle_check = False
        self.move_check = False

#-----------------------------------GameState functions ----------------------------------------------

    def flipBoard(self):
        self.board = [
            ["wR", "wN", "wB", "wK", "wQ", "wB", "wN", "wR"],
            ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],
            ["bR", "bN", "bB", "bK", "bQ", "bB", "bN", "bR"]
        ]
        self.flip = True

    def makeMove(self, move):
        self.board[move.start_row][move.start_col] = "--"
        self.board[move.end_row][move.end_col] = move.piece_moved
        self.move_log.append(move)
        self.white_to_move = not self.white_to_move
        # update parameters: castle rights, king location for checks, enpassant moves.
        if move.piece_moved == "wK":
            self.white_king_location = (move.end_row, move.end_col)
        elif move.piece_moved == "bK":
            self.black_king_location = (move.end_row, move.end_col)
        if move.is_enpassant_move:
            self.board[move.start_row][move.end_col] = "--"
        if move.is_pawn_promotion == True:
            self.board[move.end_row][move.end_col] = move.piece_moved[0] + 'Q'
        self.enpassant_square = ()
        if move.piece_moved[1] == 'p' and abs(move.start_row - move.end_row) == 2:
            self.enpassant_square = (((move.start_row + move.end_row)//2, move.end_col))
        if move.piece_moved[1] == 'K' and abs(move.start_col - move.end_col) == 2:
            self.completeCastleMove(move) 
        if not self.move_check:
            self.updateCastleRights(move)
            self.castling_rights_log.append(CastleRights(self.castling_rights.wks, self.castling_rights.bks,\
            self.castling_rights.wqs, self.castling_rights.bqs))
        self.position = self.getScore()
        
    
    

    def undoMove(self):
        if len(self.move_log) != 0:
            move = self.move_log.pop()
            self.board[move.start_row][move.start_col] = move.piece_moved
            self.board[move.end_row][move.end_col] = move.piece_captured
            self.white_to_move = not self.white_to_move
            #updating king's position
            if move.piece_moved == "wK":
                self.white_king_location = (move.start_row, move.start_col)
                if abs(move.start_col - move.end_col) == 2:
                    self.undoCastleMove(move)
            elif move.piece_moved == "bK":
                self.black_king_location = (move.start_row, move.start_col)
                if abs(move.start_col - move.end_col) == 2:
                    self.undoCastleMove(move)
            if move.is_enpassant_move:
                self.board[move.end_row][move.end_col] = "--"
                self.board[move.start_row][move.end_col] = move.piece_captured
                self.enpassant_square = (move.end_row, move.end_col)
            if move.piece_moved[1] == 'p' and abs(move.start_row - move.end_row) == 2 and len(self.move_log) != 0:
                previous_move = self.move_log[-1]
                if previous_move.piece_moved[1] == 'p' and abs(move.start_row - move.end_row) == 2:
                    self.enpassant_square = (((previous_move.start_row + previous_move.end_row)//2, move.end_col))
                else:
                    self.enpassant_square = ()
            if not self.move_check:
                self.castling_rights_log.pop()
                self.castling_rights = self.castling_rights_log[-1]
            self.check_mate = False
            self.stale_mate = False
            self.position = self.getScore()

    
    def getAllPossibleMoves(self):
        moves = []
        for r in range(len(self.board)):
            for c in range(len(self.board[r])):
                turn = self.board[r][c][0]
                if (turn == 'w' and self.white_to_move) or (turn == 'b' and not self.white_to_move):
                    piece = self.board[r][c][1]
                    if piece == 'p':
                        self.getPawnMoves(r, c, moves)
                    elif piece == 'R':
                        self.getRookMoves(r, c, moves)
                    elif piece == 'B':
                        self.getBishopMoves(r, c, moves)
                    elif piece == 'Q':
                        self.getQueenMoves(r, c, moves)
                    elif piece == 'K':
                        self.getKingMoves(r, c, moves)
                    elif piece == 'N':
                        self.getKnightMoves(r, c, moves)
        return moves

    def getValidMoves(self):
        temp_enpassant_possible = self.enpassant_square
        moves = self.getAllPossibleMoves()
        self.move_check = True
        for i in range(len(moves)-1, -1, -1):
            self.makeMove(moves[i])
            if self.inCheck():
                moves.remove(moves[i])
            self.undoMove()
        self.move_check = False
        self.enpassant_square = temp_enpassant_possible
        self.updateEndGame(moves)
        return moves

    def updateEndGame(self, moves):
        if len(moves) != 0:
            return
        self.white_to_move = not self.white_to_move
        if self.inCheck():
            self.check_mate = True
        else:
            self.stale_mate = True
        self.white_to_move = not self.white_to_move

    def completeCastleMove(self, move):
        if move.end_col == 6:
            rook_moved = self.board[move.start_row][7]
            self.board[move.start_row][7] = "--"
            self.board[move.start_row][5] = rook_moved
        else:
            rook_moved = self.board[move.start_row][0]
            self.board[move.start_row][0] = "--"
            self.board[move.start_row][3] = rook_moved

    def undoCastleMove(self, move):
        if move.end_col == 6:
            rook_moved = self.board[move.start_row][5]
            self.board[move.start_row][7] = rook_moved
            self.board[move.start_row][5] = "--"
        else:
            rook_moved = self.board[move.start_row][3]
            self.board[move.start_row][0] = rook_moved
            self.board[move.start_row][3] = "--"

    def inCheck(self):        
        if not self.white_to_move:
            return self.squareUnderAttack(self.white_king_location[0], self.white_king_location[1])
        else:
            return self.squareUnderAttack(self.black_king_location[0], self.black_king_location[1])
    
    def squareUnderAttack(self, r, c):
        opp_moves = self.getAllPossibleMoves()
        for move in opp_moves:
            if move.end_row == r and move.end_col == c:
                return True            
        return False


#------------------------------------------piece move functions------------------------------------------------------
 
    def getKnightMoves(self, r, c, moves):
        steps = ((2, 1), (2, -1), (-2, 1), (-2, -1), (1, 2), (1, -2), (-1, 2), (-1, -2))
        for step in steps:
            end_row = r + step[0]
            end_col = c + step[1]
            if 0 <= end_row <= 7 and 0 <= end_col <= 7:
                if self.board[end_row][end_col][0] != self.board[r][c][0]:   
                    moves.append(Move((r, c), (end_row, end_col), self.board))

    def getKingMoves(self, r, c, moves):
        color = self.board[r][c][0]
        for i in range(-1, 2):
            for j in range(-1, 2):
                end_row = r + i
                end_col = c + j
                if 0 <= end_row <= 7 and 0 <= end_col <= 7:
                    if self.board[end_row][end_col][0] != color:
                        if r != end_row or c != end_col:
                            moves.append(Move((r, c), (end_row, end_col), self.board))
        if self.castle_check == False:
            self.getCastleMoves(r, c, moves)

    def getCastleMoves(self, r, c, moves):
        self.castle_check = True
        self.white_to_move = not self.white_to_move
        king_side = True
        queen_side = False
        if self.is_castle_legal(king_side):
            moves.append(Move((r, c), (r, c+2), self.board))
        if self.is_castle_legal(queen_side):
            moves.append(Move((r, c), (r, c-2), self.board))
        self.white_to_move = not self.white_to_move
        self.castle_check = False
    
    def is_castle_legal(self, king_side):
        squares_to_check = ()
        if not self.white_to_move and king_side and self.castling_rights.wks:
            squares_to_check = ((7, 4), (7, 5), (7, 6))
        if self.white_to_move and king_side and self.castling_rights.bks:
            squares_to_check = ((0, 4), (0, 5), (0, 6))
        if not self.white_to_move and not king_side and self.castling_rights.wqs:
            squares_to_check = ((7, 4), (7, 3), (7, 2))
        if self.white_to_move and not king_side and self.castling_rights.bqs:
            squares_to_check = ((0, 4), (0, 3), (0, 2))
        if len(squares_to_check) == 0:
            return False
        for square in squares_to_check:
            if self.squareUnderAttack(square[0], square[1]):
                return False
            if square[1] != 4 and self.board[square[0]][square[1]] != "--":
                return False
        return True

    def getBishopMoves(self, r, c, moves):
        directions = ((1, 1), (-1, -1), (-1, 1), (1, -1))
        enemy_color = "b"
        if not self.white_to_move:
            enemy_color = "w"
        for d in directions:
            for i in range(1, 8):
                end_row = r + i*d[0]
                end_col = c + i*d[1]
                if 0 <= end_row <= 7 and 0 <= end_col <= 7:
                    if self.board[end_row][end_col] == "--":
                        moves.append(Move((r, c), (end_row, end_col), self.board))
                    elif self.board[end_row][end_col][0] == enemy_color:
                        moves.append(Move((r, c), (end_row, end_col), self.board))
                        break
                    else:
                        break
                else:
                    break

    def getRookMoves(self, r, c, moves):
        directions = ((1, 0), (-1, 0), (0, 1), (0, -1))
        enemy_color = "b"
        if not self.white_to_move:
            enemy_color = "w"
        for d in directions:
            for i in range(1, 8):
                end_row = r + i*d[0]
                end_col = c + i*d[1]
                if 0 <= end_row <= 7 and 0 <= end_col <= 7:
                    if self.board[end_row][end_col] == "--":
                        moves.append(Move((r, c), (end_row, end_col), self.board))
                    elif self.board[end_row][end_col][0] == enemy_color:
                        moves.append(Move((r, c), (end_row, end_col), self.board))
                        break
                    else:
                        break
                else:
                    break

    def getQueenMoves(self, r, c, moves):
        self.getBishopMoves(r, c, moves)
        self.getRookMoves(r, c, moves)
        
    def getPawnMoves(self, r, c, moves):
        white_start_row = 1 if self.flip else 6
        black_start_row = 6 if self.flip else 1
        color = self.board[r][c][0]
        start_row = white_start_row if color == 'w' else black_start_row
        enemy_color = 'w' if color == 'b' else 'b'
        up = self.white_to_move
        up = not up if self.flip else up
        direction = 1 if not up else -1
        steps = ((direction, 1), (direction, -1))
        for step in steps:
            end_row = r + step[0]
            end_col = c + step[1]
            if 0 <= end_row <= 7 and 0 <= end_col <= 7 and self.board[end_row][end_col][0] == enemy_color:
                moves.append(Move((r, c), (end_row, end_col), self.board))
            elif (end_row, end_col) == self.enpassant_square:
                moves.append(Move((r, c), (end_row, end_col), self.board, True))
        if self.board[r+direction][c] == "--":
            moves.append(Move((r, c), (r+direction, c), self.board))
            if r == start_row and self.board[r+direction*2][c] == "--":
                moves.append(Move((r, c), (r+direction*2, c), self.board))

    def updateCastleRights(self, move):
        if move.piece_moved == "wK":
            self.castling_rights.wks = False
            self.castling_rights.wqs = False
        elif move.piece_moved == "bK":
            self.castling_rights.bks = False
            self.castling_rights.bqs = False
        elif move.piece_moved == "wR":
            if move.start_col == 7:
                self.castling_rights.wks = False
            if move.start_col == 0:
                self.castling_rights.wqs = False
        elif move.piece_moved == "bR":
            if move.start_col == 7:
                self.castling_rights.bks = False
            if move.start_col == 0:
                self.castling_rights.bqs = False
    

    #----------------------------------------------------Minimax functions ---------------------------------------------------------

    # reurns the score of the current position based on pieces importance    
    def getScore(self):
        piece_to_value = {"K": 1000, "Q": 9, "p": 1, "N": 3, "B": 3.25, "R": 5}
        color_to_value = {"w": 1, "b": -1}
        position_value = 0
        for r in range(len(self.board)):
            for c in range(len(self.board[r])):
                piece = self.board[r][c]
                if piece != "--":
                    color_value = color_to_value[piece[0]]
                    piece_value = color_value * piece_to_value[self.board[r][c][1]]
                    position_value += piece_value
        return position_value
    

    #returns the best score for white according to minimax 
    def getMaxScore(self, depth):
        if depth == 0:
            return self.getScore()
        if self.check_mate:
            if self.white_to_move:
                return -100
            return 100
        valid_moves = self.getValidMoves()
        if len(valid_moves) == 0:
            return 0
        self.makeMove(valid_moves[0])
        best_score = self.getMinScore(depth-1)
        self.undoMove()
        for move in valid_moves:
            self.makeMove(move)
            score = self.getMinScore(depth-1)
            if score > best_score:
                best_score = score
            self.undoMove()
        return best_score

    # returns the best score for black according to minimax
    def getMinScore(self, depth):
        if depth == 0:
            return self.getScore()
        if self.check_mate:
            if self.white_to_move:
                return -100
            return 100
        if self.stale_mate:
            return 0 
        valid_moves = self.getValidMoves()
        if len(valid_moves) == 0:
            return 0
        self.makeMove(valid_moves[0])
        best_score = self.getMaxScore(depth-1)
        self.undoMove()
        for move in valid_moves:
            self.makeMove(move)
            score = self.getMaxScore(depth-1)
            if score < best_score:
                best_score = score
            self.undoMove()
        return best_score

    #returns the best move to play in the position according to minimax
    def getBestMove(self, depth):
        valid_moves = self.getValidMoves()
        self.makeMove(valid_moves[0])
        best_score = self.getScore()
        best_move = valid_moves[0]
        self.undoMove()
        for move in valid_moves:
            self.makeMove(move)
            if self.white_to_move:
                score = self.getMinScore(depth-1)
                if score < best_score:
                    best_score = score
                    best_move = move
            else:
                score = self.getMaxScore(depth-1)
                if score > best_score:
                    best_score = score
                    best_move = move
            self.undoMove()
        print(best_move.start_row ,",", best_move.start_col, " to ", best_move.end_row, ",", best_move.end_col , " gives the best score of ", best_score)
        return best_move


class CastleRights:
    def __init__(self, wks, bks, wqs, bqs):
        self.wks = wks
        self.bks = bks
        self.wqs = wqs
        self.bqs = bqs

#---------------------------------------------------------class Move ------------------------------------------------------

class Move():
    ranks_to_rows = {"1":7, "2":6, "3":5, "4":4, "5":3, "6":2, "7":1, "8":0}
    rows_to_ranks = {v: k for k, v in ranks_to_rows.items()}
    files_to_cols = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}
    cols_to_files = {v: k for k, v in files_to_cols.items()}

    def __init__(self, start_sq, end_sq, board, is_enpassant_move = False):
        self.start_row = start_sq[0]
        self.start_col = start_sq[1]
        self.end_row = end_sq[0]
        self.end_col = end_sq[1]
        self.piece_moved = board[self.start_row][self.start_col]
        self.piece_captured = board[self.end_row][self.end_col]
        self.is_pawn_promotion = (self.piece_moved[1] == "p" and self.end_row == 0) or (self.piece_moved[1] == "p" and self.end_row == 7)
        self.is_enpassant_move = is_enpassant_move
        if is_enpassant_move:            
            self.piece_captured = board[self.start_row][self.end_col]

    
    def __eq__(self, other):
        if isinstance(other, Move):
            self_id = self.getChessNotation()
            other_id = other.getChessNotation()
            if self_id == other_id:
                return True
        return False 

    def getChessNotation(self):
        return (self.getRankAndFile(self.start_row, self.start_col) + self.getRankAndFile(self.end_row, self.end_col))

    def getRankAndFile(self, r, c):
        return self.cols_to_files[c] + self.rows_to_ranks[r]


