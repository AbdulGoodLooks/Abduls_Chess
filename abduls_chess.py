# Coded by Abdul.
# Chess.

#Imports
import pygame, sys
import os
from pygame.locals import *

#compilation code
def resource_path(relative_path):
    try:
    # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

pygame.init() #Initialise pygame
fpsClock = pygame.time.Clock()

#exceptions
class CoordinateError(Exception):
    pass   
class PieceError(Exception):
    pass
class MoveError(Exception):
    pass

#Chess pieces
pawn, knight, bishop, rook, queen, king = 'pawn', 'knight', 'bishop', 'rook', 'queen', 'king'
list_of_chess_pieces = [] #This is the list of instances of the class chessPiece that are on the board.
list_of_valid_moves = []

#Chess coordinates
a, b, c, d, e, f, g, h = 1, 2, 3, 4, 5, 6, 7, 8 #this allows you to notate e, 5 or c, 6 similar to actual chess notation

#icons
black_pawn   = pygame.image.load(  'black_pawn.png')
white_pawn   = pygame.image.load(  'white_pawn.png')
black_knight = pygame.image.load('black_knight.png')
white_knight = pygame.image.load('white_knight.png')
black_bishop = pygame.image.load('black_bishop.png')
white_bishop = pygame.image.load('white_bishop.png')
black_rook   = pygame.image.load(  'black_rook.png')
white_rook   = pygame.image.load(  'white_rook.png')
black_queen  = pygame.image.load( 'black_queen.png')
white_queen  = pygame.image.load( 'white_queen.png')
black_king   = pygame.image.load(  'black_king.png')
white_king   = pygame.image.load(  'white_king.png')

# Variable Declarations
FPS = 15
fps_clock = pygame.time.Clock()
window_height = 720
window_width  = 1280
board_size = 720
board_x    = 0 + (window_width - board_size) / 2
board_y    = 0
mouse_x    = 0
mouse_y    = 0
tile_size  = 91 #The size of each tile in pixel
list_of_capturable_pieces = []
list_of_valid_enpassants  = []
a_piece_is_selected       = False
white_king_has_moved      = False
black_king_has_moved      = False
white_king_is_in_check    = False
black_king_is_in_check    = False
next_one_move_per_turn    = True
flash_counter = 0
white_in_check_mate = False
black_in_check_mate = False
#reset button variables
reset_button_width  = 190
reset_button_height = 90
reset_button_gap    = 10
reset_button_x = window_width  - reset_button_width  - reset_button_gap
reset_button_y = window_height - reset_button_height - reset_button_gap
#one move per turn button.
one_move_button_width  = 190
one_move_button_height = 90
one_move_button_gap    = 10
one_move_button_x = reset_button_x
one_move_button_y = reset_button_y - one_move_button_height - one_move_button_gap
#victory button
victory_button_width  = 500
victory_button_height = 180
victory_button_gap    = 10
victory_button_x = window_width / 2 - victory_button_width / 2
victory_button_y = window_height / 2 - victory_button_height / 2

#Danger tile
# A danger tile is a tile that an enemy move can see.
# This is used for knowing which moves would put the King in danger.
# They are needed inside the get_valid_moves in king move processing
white_danger_tiles = [] # Tiles which black pieces can see.
black_danger_tiles = [] # Tiles which black pieces can see.

#color                 R    G    B    Transparency
glass_blue        = (165, 178, 193, 128) 
glass_blue        = (165, 178, 193, 200) 
black             = (  0,   0,   0)
dark_theme        = ( 25,  25,  25)
dark_grey         = ( 90,  90,  90)
red               = (255,   0,   0)
green             = (  0, 255,   0)
yellow            = (255, 255,   0)
brown             = (155,   0,   0)
light_yellow      = (255, 255, 125)
very_light_yellow = (255, 255, 175)
blue              = (  0,   0, 255)
white             = (255, 255, 255)

next_turn = white #White starts first.

# board_coordinate is a coordinate system used by the pieces.
def convert_into_board_coordinate(x, y):
    if x >= board_x and x <= board_x + board_size and y >= 0 and y <= window_height:
        x = x - board_x
        y = y - board_y
        board_coordinate_x = int(x / tile_size)
        board_coordinate_y = int(y / tile_size)

        board_coordinate_x += 1 #start counting from 1 and not 0
        board_coordinate_y += 1 #start counting from 1 and not 0

        return board_coordinate_x, board_coordinate_y
    else:
        raise CoordinateError

def convert_into_pixel_coordinate(x, y):
    if x >= 1 and x <= 8 and y >= 1 and y <= 8: #8 is the number of tiles on the board in each direction
        x = x-1 #start counting from 1 and not 0
        y = y-1 #start counting from 1 and not 0

        x = x * tile_size
        x += board_x
        y = y * tile_size
        y += board_y #board_y is 0 at this resolution so this does nothing. 
        
        return x, y 
    else:
        raise CoordinateError

def highlight_tile(drawing_x, drawing_y = None, color = light_yellow):
    if type(drawing_x) == tuple: #If drawing_x was a coordinate use that as the coordinates and leave drawing_y untouched
        tile_highlight = pygame.Rect(drawing_x, (tile_size, tile_size))
        pygame.draw.rect(default_surface, color, tile_highlight)
    else: #Otherwise (drawing_x, drawing_x) is the coordinate
        tile_highlight = pygame.Rect((drawing_x, drawing_y), (tile_size, tile_size))
        pygame.draw.rect(default_surface, color, tile_highlight)
    
    # The reason for that rather unintuitive approach is to allow this function to take in two variables or take in a single variable
    # that is a tuple of two numbers, and still give the correct output without need for unpacking and stuff later on.

def is_mouse_over_a_tile(mouse_x, mouse_y):
    try:
        mouse_board_x, mouse_board_y = convert_into_board_coordinate(mouse_x, mouse_y) #Convert the mouse's location into board coordinates
        drawing_x, drawing_y = convert_into_pixel_coordinate(mouse_board_x, mouse_board_y) #Get the top left corner of the board
        #(This draws it but opaque.) highlight_tile(drawing_x, drawing_y, glass_blue) #Use it to draw the highlight
        mouse_surface = pygame.Surface((tile_size, tile_size), pygame.SRCALPHA)
        mouse_surface.fill(glass_blue)
        default_surface.blit(mouse_surface, (drawing_x, drawing_y))

    except CoordinateError:
        return False
    
    return True

def get_highlighted_tile(mouse_x, mouse_y):
    if is_mouse_over_a_tile(mouse_x, mouse_y) == True:
        mouse_board_x, mouse_board_y = convert_into_board_coordinate(mouse_x, mouse_y) #Convert the mouse's location into board coordinates
        return (mouse_board_x, mouse_board_y)
    else:
        return

def go_in_a_direction(board_x, board_y, direction):
    direction_x, direction_y = direction[0], direction[1]
    board_x, board_y = (board_x + direction_x), (board_y + direction_y)
    return board_x, board_y 
    
def get_valid_moves(piece_type:str, board_coordinate:tuple, color:str, a_piece_is_selected, white_danger_tiles, black_danger_tiles, piece_object, highlighting = True): #big boi function :)
    # This function is essentially the entire game's rules engine.
    # It will return the list of valid moves. the list of capturable pieces and the list of enpassants.
    list_of_valid_moves = []
    list_of_capturable_pieces = []
    list_of_valid_enpassants = []
    piece_in_front = False
    piece_two_tiles_in_front = False
    board_x, board_y = board_coordinate[0], board_coordinate[1]

    if a_piece_is_selected == False:
        return list_of_valid_moves, list_of_capturable_pieces, list_of_valid_enpassants #If nothing is selected, return empty lists.
    
    # Check if the kings are in check
    white_king_is_in_check = is_king_in_check(white, white_danger_tiles)
    black_king_is_in_check = is_king_in_check(black, black_danger_tiles)

    #Pawn move processing
    if piece_type == pawn:
        #Pawns move forward once, and can move forward twice on their first move.
        for piece in list_of_chess_pieces: #piece infront of us?
            piece_board_x, piece_board_y = piece.board_coordinate[0], piece.board_coordinate[1]
            if ((piece_board_y == board_y + 1 and color == black) or (piece_board_y == board_y - 1 and color == white)) and piece_board_x == board_x:
                piece_in_front = True
            if ((piece_board_y == board_y + 2 and color == black) or (piece_board_y == board_y - 2 and color == white)) and piece_board_x == board_x:
                piece_two_tiles_in_front = True

        if piece_in_front == False:#Tile directly infront is a valid move. Add to the list.
            if color == black:
                list_of_valid_moves.append((board_x, (board_y + 1))) 
            else:
                list_of_valid_moves.append((board_x, (board_y - 1)))

        if (board_y == 2 and color == black) or (board_y == 7 and color == white): #is first move?
           first_move = True
        else:
            first_move = False

        if first_move == True and piece_two_tiles_in_front == False and piece_in_front == False:
            if color == black:
                list_of_valid_moves.append((board_x, (board_y + 2)))
            else:
                list_of_valid_moves.append((board_x, (board_y - 2))) 
    
        #check if there is a piece that can be captured
        if color == black:
            pawn_capture_tiles = ((board_x + 1), (board_y + 1)), ((board_x - 1), (board_y + 1))
        else:
            pawn_capture_tiles = ((board_x + 1), (board_y - 1)), ((board_x - 1), (board_y - 1))
        for piece in list_of_chess_pieces:
            if piece.board_coordinate in pawn_capture_tiles and piece.color != color:
                list_of_capturable_pieces.append(piece.board_coordinate)

        #EN PASSANT
        # If an enemy piece moves two tiles forwards in one move, pawns can perform enpassant.
        # En passant allows pawns to capture another pawn as if it only moves one tile.
        if color == black:
            if board_y == 5: #We are on the 3rd rank.
                # The tiles we check for enpassant are one tile to the left & one tile to the right of us.
                enpassant_tiles = (((board_x + 1), board_y), ((board_x - 1), board_y))
                for piece in list_of_chess_pieces: # Go through every piece on the board and check if ...
                    #... if the piece both an enemy and in the correct position
                    if piece.board_coordinate in enpassant_tiles and piece.color == white and piece.piece_type == pawn:
                        # add that tile to the enpassant tiles.
                        en_passant_x, en_passant_y = piece.board_coordinate[0], (piece.board_coordinate[1] + 1)
                        enpassant_tile = (en_passant_x, en_passant_y)
                        list_of_valid_enpassants.append(enpassant_tile)
                        list_of_capturable_pieces.append(enpassant_tile)


        else:
            if board_y == 4: #We are on the 5th rank.
                enpassant_tiles = (((board_x + 1), board_y), ((board_x - 1), board_y))
                for piece in list_of_chess_pieces: # Go through every piece on the board and check if ...
                    #... if the piece both an enemy and in the correct position 
                    if piece.board_coordinate in enpassant_tiles and piece.color == black and piece.piece_type == pawn:
                        # add that tile to the enpassant tiles.
                        en_passant_x, en_passant_y = piece.board_coordinate[0], (piece.board_coordinate[1] - 1)
                        enpassant_tile = (en_passant_x, en_passant_y)
                        list_of_valid_enpassants.append(enpassant_tile)
                        list_of_capturable_pieces.append(enpassant_tile)
            
    #Knight move proceesing
    if piece_type == knight:
        #Knights move 2 spaces in a direction, and then a single space perpedicularly to that direction
        #Knights can jump over pieces.
        valid_knight_moves = [(board_x + 2, board_y + 1),
        (board_x + 2, board_y - 1), # This also
        (board_x - 2, board_y + 1),
        (board_x - 2, board_y - 1),
        (board_x + 1, board_y + 2),
        (board_x + 1, board_y - 2),
        (board_x - 1, board_y + 2),
        (board_x - 1, board_y - 2)] # // Wierd bug, the last value in this list isn't being acessesed... SOMEONE FIX PLEASE I BEG YOU>>>>

        #check if the jumping tile is occupied
        for move in valid_knight_moves: #for each coordinate (tuple) in the list valid_knight_move
            blocked = False
            for piece in list_of_chess_pieces:  #go through every piece on the board and see if it's coordinate matches the move
                if piece.board_coordinate == move:
                    blocked = True
                    if piece.color != color:   
                        list_of_capturable_pieces.append(move)
            if blocked == False:
                list_of_valid_moves.append(move)
                    
    #Bishop move processing
    if piece_type == bishop or piece_type == queen:
        #bishops can move diagonally an infinite number of spaces, but cannot jump over other pieces
        down_right, down_left, up_right, up_left = (1, 1), (-1, 1), (1, -1), (-1, -1)
        list_of_diagonal_directions = (down_right, down_left, up_right, up_left)
        #iteratively go in one direction until we find an obstacle
        for move_direction in list_of_diagonal_directions:
            board_x, board_y = board_coordinate[0], board_coordinate[1]
            direction = move_direction
            in_bounds, blocked = True, False
            while in_bounds == True and blocked == False:
                board_x, board_y = go_in_a_direction(board_x, board_y, direction)
                #check if its in bounds
                if board_x >= 1 and board_x <= 8 and board_y >= 1 and board_y <= 8:
                    in_bounds = True
                    #check if its blocked
                    for piece in list_of_chess_pieces:
                        if piece.board_coordinate == (board_x, board_y):
                            blocked = True
                            if piece.color != color:
                                list_of_capturable_pieces.append((board_x, board_y))
                            break
                    if blocked == False:
                        list_of_valid_moves.append((board_x, board_y))
                else:
                    in_bounds = False

    #Rook move processing
    if piece_type == rook or piece_type == queen:
        #Rooks can move in a straight line an ubnlimited number of spaces.
        #Rooks cannot jump over other pieces.
        up, down, left, right = (0, -1), (0, 1), (-1, 0), (1, 0)
        list_of_directions = (up, down, left, right) 
        for move_direction in list_of_directions:
            board_x, board_y = board_coordinate[0], board_coordinate[1]
            direction = move_direction
            in_bounds, blocked = True, False
            while in_bounds == True and blocked == False:
                board_x, board_y = go_in_a_direction(board_x, board_y, direction)
                #check if its in bounds
                if board_x >= 1 and board_x <= 8 and board_y >= 1 and board_y <= 8:
                    in_bounds = True
                    #check if its blocked
                    for piece in list_of_chess_pieces:
                        if piece.board_coordinate == (board_x, board_y):
                            blocked = True
                            if piece.color != color:
                                list_of_capturable_pieces.append((board_x, board_y))
                            break
                    if blocked == False:
                        list_of_valid_moves.append((board_x, board_y))
                else:
                    in_bounds = False

   #King move processing
    if piece_type == king:
        list_of_valid_moves = []
        possible_moves = [((board_x +  1), (board_y +  1)),
                          ((board_x +  0), (board_y +  1)),
                          ((board_x + -1), (board_y +  1)),
                          ((board_x + -1), (board_y +  0)),
                          ((board_x + -1), (board_y + -1)),
                          ((board_x +  0), (board_y + -1)),
                          ((board_x +  1), (board_y + -1)),
                          ((board_x +  1), (board_y +  0)) ]
        blocked = False

        for move in possible_moves:
            for piece in list_of_chess_pieces:
                blocked = False
                if move == piece.board_coordinate:
                    blocked = True
                    if piece.color != color:
                        list_of_capturable_pieces.append(move)
                    break
            if blocked == False:
                list_of_valid_moves.append(move)
        
        #Castling.
        can_castle_queen_side = True
        can_castle_king_side = True
        if color == black:
            if black_king_has_moved == False and black_king_is_in_check == False:
                #check the king side
                list_of_tiles_between_king_and_rook = [(6, 1), (7, 1)]
                # do not let the king castle if the tiles are blocked or are seen by enemies
                for tile in list_of_tiles_between_king_and_rook:
                    if tile in black_danger_tiles:
                        can_castle_king_side = False
                for piece in list_of_chess_pieces:
                    if piece.board_coordinate in list_of_tiles_between_king_and_rook:
                        can_castle_king_side = False
                #check the queen side
                list_of_tiles_between_king_and_rook = [(2, 1), (3, 1), (4, 1)]
                # do not let the king castle if the tiles are blocked or are seen by enemies
                for tile in list_of_tiles_between_king_and_rook:
                    if tile in black_danger_tiles:
                        can_castle_queen_side = False
                for piece in list_of_chess_pieces:
                    if piece.board_coordinate in list_of_tiles_between_king_and_rook:
                        can_castle_queen_side = False

                if can_castle_king_side == True:
                    list_of_valid_moves.append((7, 1))
                if can_castle_queen_side == True:
                    list_of_valid_moves.append((3, 1))
        else:
            if white_king_has_moved == False and white_king_is_in_check == False:
                #check the king side
                list_of_tiles_between_king_and_rook = [(6, 8), (7, 8)]
                # do not let the king castle if the tiles are blocked or are seen by enemies
                for tile in list_of_tiles_between_king_and_rook:
                    if tile in white_danger_tiles:
                        can_castle_king_side = False
                for piece in list_of_chess_pieces:
                    if piece.board_coordinate in list_of_tiles_between_king_and_rook:
                        can_castle_king_side = False
                #check the queen side
                list_of_tiles_between_king_and_rook = [(2, 8), (3, 8), (4, 8)]
                # do not let the king castle if the tiles are blocked or are seen by enemies
                for tile in list_of_tiles_between_king_and_rook:
                    if tile in white_danger_tiles:
                        can_castle_queen_side = False
                for piece in list_of_chess_pieces:
                    if piece.board_coordinate in list_of_tiles_between_king_and_rook:
                        can_castle_queen_side = False

                if can_castle_king_side == True:
                    list_of_valid_moves.append((7, 8))
                if can_castle_queen_side == True:
                    list_of_valid_moves.append((3, 8))
        
        # Check if the tiles the king can move to are safe ie. no enemy piece can capture there
        reference_list = list_of_valid_moves.copy()               # Returns a shallow copy of the list. This is essential to prevent bugs

        # Dont let the king move to a danger tile. 
        for move in reference_list:
            if color == black:
                if move in black_danger_tiles:
                    list_of_valid_moves.remove(move)
            else:
                if move in white_danger_tiles:
                    list_of_valid_moves.remove(move)

        #Do not let the king capture a defended piece
        reference_list = list_of_capturable_pieces.copy()
        for move in reference_list:
            if color == black:
                if move in black_danger_tiles:
                    list_of_capturable_pieces.remove(move)
            else:
                if move in white_danger_tiles:
                    list_of_capturable_pieces.remove(move)

    #remove out of bounds moves
    list_of_inbound_valid_moves = []
    for move in list_of_valid_moves:
        move_x, move_y = move[0], move[1]
        if move_x >= 1 and move_x <= 8 and move_y >= 1 and move_y <= 8:
            list_of_inbound_valid_moves.append(move)

    #remove moves that put the king in check
    illegal_moves = get_moves_that_would_put_the_king_in_check(piece_object, white_danger_tiles, black_danger_tiles)
    safe_valid_inbound_valid_moves = [] # Safe means that it won't put your own king in check
    safe_captures = []
    for move in list_of_inbound_valid_moves:
        if move not in illegal_moves:
            safe_valid_inbound_valid_moves.append(move) #remove moves that put your own king in check
    for move in list_of_capturable_pieces:
        if move not in illegal_moves:
            safe_captures.append(move)


    list_of_valid_moves = safe_valid_inbound_valid_moves
    list_of_capturable_pieces = safe_captures

    #highlight pieces that can be captured

    if highlighting == True:
        if a_piece_is_selected == True: #if a piece is selected that is
            for tile in list_of_capturable_pieces:
                pixel_x, pixel_y = convert_into_pixel_coordinate(*tile)
                highlight_tile(pixel_x, pixel_y, red)
                
    return list_of_valid_moves, list_of_capturable_pieces, list_of_valid_enpassants

def get_theoretical_valid_moves(piece_type:str, board_coordinate:tuple, color:str, a_piece_is_selected, white_danger_tiles, black_danger_tiles):
    # clone of get_valid_move to be used inside the calculate_danger_tile function, instead of get_valid_moves to prevent infinite recursion.
    list_of_valid_moves = []
    list_of_capturable_pieces = []
    list_of_valid_enpassants = []
    piece_in_front = False
    piece_two_tiles_in_front = False
    board_x, board_y = board_coordinate[0], board_coordinate[1]

    if a_piece_is_selected == False:
        return list_of_valid_moves, list_of_capturable_pieces, list_of_valid_enpassants #If nothing is selected, return empty lists.

    #Pawn move processing
    if piece_type == pawn:
        #Pawns move forward once, and can move forward twice on their first move.
        for piece in list_of_chess_pieces: #piece infront of us?
            piece_board_x, piece_board_y = piece.board_coordinate[0], piece.board_coordinate[1]
            if ((piece_board_y == board_y + 1 and color == black) or (piece_board_y == board_y - 1 and color == white)) and piece_board_x == board_x:
                piece_in_front = True
            if ((piece_board_y == board_y + 2 and color == black) or (piece_board_y == board_y - 2 and color == white)) and piece_board_x == board_x:
                piece_two_tiles_in_front = True

        if piece_in_front == False:#Tile directly infront is a valid move. Add to the list.
            if color == black:
                list_of_valid_moves.append((board_x, (board_y + 1))) 
            else:
                list_of_valid_moves.append((board_x, (board_y - 1)))

        if (board_y == 2 and color == black) or (board_y == 7 and color == white): #is first move?
           first_move = True
        else:
            first_move = False

        if first_move == True and piece_two_tiles_in_front == False and piece_in_front == False:
            if color == black:
                list_of_valid_moves.append((board_x, (board_y + 2)))
            else:
                list_of_valid_moves.append((board_x, (board_y - 2))) 
    
        #check if there is a piece that can be captured
        if color == black:
            pawn_capture_tiles = ((board_x + 1), (board_y + 1)), ((board_x - 1), (board_y + 1))
        else:
            pawn_capture_tiles = ((board_x + 1), (board_y - 1)), ((board_x - 1), (board_y - 1))
        for piece in list_of_chess_pieces:
            if piece.board_coordinate in pawn_capture_tiles and piece.color != color:
                list_of_capturable_pieces.append(piece.board_coordinate)

        #EN PASSANT
        # If an enemy piece moves two tiles forwards in one move, pawns can perform enpassant.
        # En passant allows pawns to capture another pawn as if it only moves one tile.
        if color == black:
            if board_y == 5: #We are on the 3rd rank.
                # The tiles we check for enpassant are one tile to the left & one tile to the right of us.
                enpassant_tiles = (((board_x + 1), board_y), ((board_x - 1), board_y))
                for piece in list_of_chess_pieces: # Go through every piece on the board and check if ...
                    #... if the piece both an enemy and in the correct position
                    if piece.board_coordinate in enpassant_tiles and piece.color == white and piece.piece_type == pawn:
                        # add that tile to the enpassant tiles.
                        en_passant_x, en_passant_y = piece.board_coordinate[0], (piece.board_coordinate[1] + 1)
                        enpassant_tile = (en_passant_x, en_passant_y)
                        list_of_valid_enpassants.append(enpassant_tile)
                        list_of_capturable_pieces.append(enpassant_tile)


        else:
            if board_y == 4: #We are on the 5th rank.
                enpassant_tiles = (((board_x + 1), board_y), ((board_x - 1), board_y))
                for piece in list_of_chess_pieces: # Go through every piece on the board and check if ...
                    #... if the piece both an enemy and in the correct position
                    if piece.board_coordinate in enpassant_tiles and piece.color == black and piece.piece_type == pawn:
                        # add that tile to the enpassant tiles.
                        en_passant_x, en_passant_y = piece.board_coordinate[0], (piece.board_coordinate[1] - 1)
                        enpassant_tile = (en_passant_x, en_passant_y)
                        list_of_valid_enpassants.append(enpassant_tile)
                        list_of_capturable_pieces.append(enpassant_tile)
            
    #Knight move proceesing
    if piece_type == knight:
        #Knights move 2 spaces in a direction, and then a single space perpedicularly to that direction
        #Knights can jump over pieces.
        valid_knight_moves = [(board_x + 2, board_y + 1),
        (board_x + 2, board_y - 1), # This also
        (board_x - 2, board_y + 1),
        (board_x - 2, board_y - 1),
        (board_x + 1, board_y + 2),
        (board_x + 1, board_y - 2),
        (board_x - 1, board_y + 2),
        (board_x - 1, board_y - 2)] # // Wierd bug, the last value in this list isn't being acessesed... SOMEONE FIX PLEASE I BEG YOU>>>>

        #check if the jumping tile is occupied
        for move in valid_knight_moves: #for each coordinate (tuple) in the list valid_knight_move
            blocked = False
            for piece in list_of_chess_pieces:  #go through every piece on the board and see if it's coordinate matches the move
                if piece.board_coordinate == move:
                    blocked = True
                    if piece.color != color:   
                        list_of_capturable_pieces.append(move)
            if blocked == False:
                list_of_valid_moves.append(move)
                    
    #Bishop move processing
    if piece_type == bishop or piece_type == queen:
        #bishops can move diagonally an infinite number of spaces, but cannot jump over other pieces
        down_right, down_left, up_right, up_left = (1, 1), (-1, 1), (1, -1), (-1, -1)
        list_of_diagonal_directions = (down_right, down_left, up_right, up_left)
        #iteratively go in one direction until we find an obstacle
        for move_direction in list_of_diagonal_directions:
            board_x, board_y = board_coordinate[0], board_coordinate[1]
            direction = move_direction
            in_bounds, blocked = True, False
            while in_bounds == True and blocked == False:
                board_x, board_y = go_in_a_direction(board_x, board_y, direction)
                #check if its in bounds
                if board_x >= 1 and board_x <= 8 and board_y >= 1 and board_y <= 8:
                    in_bounds = True
                    #check if its blocked
                    for piece in list_of_chess_pieces:
                        if piece.board_coordinate == (board_x, board_y):
                            blocked = True
                            if piece.color != color:
                                list_of_capturable_pieces.append((board_x, board_y))
                            break
                    if blocked == False:
                        list_of_valid_moves.append((board_x, board_y))
                else:
                    in_bounds = False

    #Rook move processing
    if piece_type == rook or piece_type == queen:
        #Rooks can move in a straight line an ubnlimited number of spaces.
        #Rooks cannot jump over other pieces.
        up, down, left, right = (0, -1), (0, 1), (-1, 0), (1, 0)
        list_of_directions = (up, down, left, right) 
        for move_direction in list_of_directions:
            board_x, board_y = board_coordinate[0], board_coordinate[1]
            direction = move_direction
            in_bounds, blocked = True, False
            while in_bounds == True and blocked == False:
                board_x, board_y = go_in_a_direction(board_x, board_y, direction)
                #check if its in bounds
                if board_x >= 1 and board_x <= 8 and board_y >= 1 and board_y <= 8:
                    in_bounds = True
                    #check if its blocked
                    for piece in list_of_chess_pieces:
                        if piece.board_coordinate == (board_x, board_y):
                            blocked = True
                            if piece.color != color:
                                list_of_capturable_pieces.append((board_x, board_y))
                            break
                    if blocked == False:
                        list_of_valid_moves.append((board_x, board_y))
                else:
                    in_bounds = False

   #King move processing
    if piece_type == king:
        list_of_valid_moves = []
        possible_moves = [((board_x +  1), (board_y +  1)),
                          ((board_x +  0), (board_y +  1)),
                          ((board_x + -1), (board_y +  1)),
                          ((board_x + -1), (board_y +  0)),
                          ((board_x + -1), (board_y + -1)),
                          ((board_x +  0), (board_y + -1)),
                          ((board_x +  1), (board_y + -1)),
                          ((board_x +  1), (board_y +  0)) ]
        blocked = False

        for move in possible_moves:
            for piece in list_of_chess_pieces:
                blocked = False
                if move == piece.board_coordinate:
                    blocked = True
                    if piece.color != color:
                        list_of_capturable_pieces.append(move)
                    break
            if blocked == False:
                list_of_valid_moves.append(move)
        
        #Castling.
        can_castle_queen_side = True
        can_castle_king_side = True
        if color == black:
            if black_king_has_moved == False and black_king_in_check == False:
                #check the king side
                list_of_tiles_between_king_and_rook = [(6, 1), (7, 1)]
                # do not let the king castle if the tiles are blocked or are seen by enemies
                for tile in list_of_tiles_between_king_and_rook:
                    if tile in black_danger_tiles:
                        can_castle_king_side = False
                for piece in list_of_chess_pieces:
                    if piece.board_coordinate in list_of_tiles_between_king_and_rook:
                        can_castle_king_side = False
                #check the queen side
                list_of_tiles_between_king_and_rook = [(2, 1), (3, 1), (4, 1)]
                # do not let the king castle if the tiles are blocked or are seen by enemies
                for tile in list_of_tiles_between_king_and_rook:
                    if tile in black_danger_tiles:
                        can_castle_queen_side = False
                for piece in list_of_chess_pieces:
                    if piece.board_coordinate in list_of_tiles_between_king_and_rook:
                        can_castle_queen_side = False

                if can_castle_king_side == True:
                    list_of_valid_moves.append((7, 1))
                if can_castle_queen_side == True:
                    list_of_valid_moves.append((3, 1))
        else:
            if white_king_has_moved == False and white_king_in_check == False:
                #check the king side
                list_of_tiles_between_king_and_rook = [(6, 8), (7, 8)]
                # do not let the king castle if the tiles are blocked or are seen by enemies
                for tile in list_of_tiles_between_king_and_rook:
                    if tile in white_danger_tiles:
                        can_castle_king_side = False
                for piece in list_of_chess_pieces:
                    if piece.board_coordinate in list_of_tiles_between_king_and_rook:
                        can_castle_king_side = False
                #check the queen side
                list_of_tiles_between_king_and_rook = [(2, 8), (3, 8), (4, 8)]
                # do not let the king castle if the tiles are blocked or are seen by enemies
                for tile in list_of_tiles_between_king_and_rook:
                    if tile in white_danger_tiles:
                        can_castle_queen_side = False
                for piece in list_of_chess_pieces:
                    if piece.board_coordinate in list_of_tiles_between_king_and_rook:
                        can_castle_queen_side = False

                if can_castle_king_side == True:
                    list_of_valid_moves.append((7, 8))
                if can_castle_queen_side == True:
                    list_of_valid_moves.append((3, 8))
        
        # Check if the tiles the king can move to are safe ie. no enemy piece can capture there
        reference_list = list_of_valid_moves.copy()               # Returns a shallow copy of the list. This is essential to prevent bugs

        # Dont let the king move to a danger tile. 
        for move in reference_list:
            if color == black:
                if move in black_danger_tiles:
                    list_of_valid_moves.remove(move)
            else:
                if move in white_danger_tiles:
                    list_of_valid_moves.remove(move)

        #Do not let the king capture a defended piece
        reference_list = list_of_capturable_pieces.copy()
        for move in reference_list:
            if color == black:
                if move in black_danger_tiles:
                    list_of_capturable_pieces.remove(move)
            else:
                if move in white_danger_tiles:
                    list_of_capturable_pieces.remove(move)

    #remove out of bounds moves
    list_of_inbound_valid_moves = []
    for move in list_of_valid_moves:
        move_x, move_y = move[0], move[1]
        if move_x >= 1 and move_x <= 8 and move_y >= 1 and move_y <= 8:
            list_of_inbound_valid_moves.append(move)
        
    list_of_valid_moves = list_of_inbound_valid_moves

    return list_of_valid_moves, list_of_capturable_pieces, list_of_valid_enpassants

def calculate_danger_tiles(piece_type:str, board_coordinate:tuple, color:str):
    # This function, allows us to get the danger tiles WITHOUT calling
    # get_valid_moves() which is generating alot of bugs when used
    # outside of the use cases it was designed for.

    # This function is a modified clone of get_valid moves
    list_of_tiles_a_piece_can_go_to = []
    board_x, board_y = board_coordinate[0], board_coordinate[1]

    #Pawn move processing
    if piece_type == pawn:    
        #Add the pawn's capture tiles to the danger zone.
        if color == black:
            pawn_capture_tiles = ((board_x + 1), (board_y + 1)), ((board_x - 1), (board_y + 1))
        else:
            pawn_capture_tiles = ((board_x + 1), (board_y - 1)), ((board_x - 1), (board_y - 1))
        
        for tile in pawn_capture_tiles:
            list_of_tiles_a_piece_can_go_to.append(tile)
          
    #Knight move proceesing
    if piece_type == knight:
        #Knights move 2 spaces in a direction, and then a single space perpedicularly to that direction
        #Knights can jump over pieces.
        valid_knight_moves = [(board_x + 2, board_y + 1),
        (board_x + 2, board_y - 1), 
        (board_x - 2, board_y + 1),
        (board_x - 2, board_y - 1),
        (board_x + 1, board_y + 2),
        (board_x + 1, board_y - 2),
        (board_x - 1, board_y + 2),
        (board_x - 1, board_y - 2)] 

        #check if the jumping tile is occupied
        for move in valid_knight_moves: #for each coordinate (tuple) in the list valid_knight_move
            blocked = False
            for piece in list_of_chess_pieces:  #go through every piece on the board and see if it's coordinate matches the move
                if piece.board_coordinate == move:
                    blocked = True
                    list_of_tiles_a_piece_can_go_to.append(move)
            if blocked == False:
                list_of_tiles_a_piece_can_go_to.append(move)
                    
    #Bishop move processing
    if piece_type == bishop or piece_type == queen:
        #bishops can move diagonally an infinite number of spaces, but cannot jump over other pieces
        down_right, down_left, up_right, up_left = (1, 1), (-1, 1), (1, -1), (-1, -1)
        list_of_diagonal_directions = (down_right, down_left, up_right, up_left)
        #iteratively go in one direction until we find an obstacle
        for move_direction in list_of_diagonal_directions:
            board_x, board_y = board_coordinate[0], board_coordinate[1]
            direction = move_direction
            in_bounds, blocked = True, False
            while in_bounds == True and blocked == False:
                board_x, board_y = go_in_a_direction(board_x, board_y, direction)
                #check if its in bounds
                if board_x >= 1 and board_x <= 8 and board_y >= 1 and board_y <= 8:
                    in_bounds = True
                    #check if its blocked
                    for piece in list_of_chess_pieces:
                        if piece.board_coordinate == (board_x, board_y) and piece.piece_type != king: #Tiles behind the king are also danger tiles
                            blocked = True
                            list_of_tiles_a_piece_can_go_to.append((board_x, board_y))
                            # Check 
                    if blocked == False:
                        list_of_tiles_a_piece_can_go_to.append((board_x, board_y))
                else:
                    in_bounds = False

    #Rook move processing
    if piece_type == rook or piece_type == queen:
        #Rooks can move in a straight line an ubnlimited number of spaces.
        #Rooks cannot jump over other pieces.
        up, down, left, right = (0, -1), (0, 1), (-1, 0), (1, 0)
        list_of_directions = (up, down, left, right) 
        for move_direction in list_of_directions:
            board_x, board_y = board_coordinate[0], board_coordinate[1]
            direction = move_direction
            in_bounds, blocked = True, False
            while in_bounds == True and blocked == False:
                board_x, board_y = go_in_a_direction(board_x, board_y, direction)
                #check if its in bounds
                if board_x >= 1 and board_x <= 8 and board_y >= 1 and board_y <= 8:
                    in_bounds = True
                    #check if its blocked
                    for piece in list_of_chess_pieces:
                        if piece.board_coordinate == (board_x, board_y) and piece.piece_type != king:
                            blocked = True
                            # in get_valid_moves it would check to see if it is an enemy. In this case do not.
                            list_of_tiles_a_piece_can_go_to.append((board_x, board_y))
                    if blocked == False: #This will cause the loop to exit.
                        list_of_tiles_a_piece_can_go_to.append((board_x, board_y))
                else:
                    in_bounds = False

   #King move processing
    if piece_type == king:
        #No matter what. Do not let the King move within 1 tile of another King.
        list_of_tiles_a_piece_can_go_to = [((board_x +  1), (board_y +  1)),
                          ((board_x +  0), (board_y +  1)),
                          ((board_x + -1), (board_y +  1)),
                          ((board_x + -1), (board_y +  0)),
                          ((board_x + -1), (board_y + -1)),
                          ((board_x +  0), (board_y + -1)),
                          ((board_x +  1), (board_y + -1)),
                          ((board_x +  1), (board_y +  0)) ]
        
    #remove out of bounds moves
    list_of_inbound_valid_moves = []
    for move in list_of_tiles_a_piece_can_go_to:
        move_x, move_y = move[0], move[1]
        if move_x >= 1 and move_x <= 8 and move_y >= 1 and move_y <= 8:
            list_of_inbound_valid_moves.append(move)
        
    list_of_tiles_a_piece_can_go_to = list_of_inbound_valid_moves

    return list_of_tiles_a_piece_can_go_to  

def change_piece(piece_type:str, board_coordinate:tuple, color:str, new_type = queen):
    # This function promotes the pawns into queens upon reaching the end of the board.
    board_y = board_coordinate[1]
    if piece_type == pawn:              # Is pawn?
        if color == white:                  # Is white?
            if board_y == 1:                    #On the Edge?
                return new_type                     # Good. Promote the pawn
            else:                               # Else do nothing
                return piece_type
        else:                          
            if board_y == 8:                    
                return new_type
            else:
                return piece_type
    else: #else do nothing
        return piece_type

def castle(clicked_tile, selected_piece, list_of_valid_moves, white_king_has_moved, black_king_has_moved):
    #Castling
    if clicked_tile in list_of_valid_moves:    #move is valid?
        if selected_piece.piece_type == king:                #its a king?
            if selected_piece.color == black and black_king_has_moved == False:                    #its black?
                if selected_piece.board_coordinate in ((7, 1), (3, 1), (5, 1)):        #The King moved to the correct tile (If this is true then it's last tile was the starting tile)
                    if clicked_tile == (7, 1):                 #we clicked on a tile to castle kingside? (We know this move is valid, so castling is allowed)
                        list_of_valid_moves = [(6, 1)] #Ensure the rook moves.
                        black_right_rook.move_piece((6, 1), list_of_valid_moves)          #move the rook, then exit this if-block for the king to move normally
                    elif clicked_tile == (3, 1):               #we clicked on a tile to castle queenside.
                        list_of_valid_moves = [(4, 1)]
                        black_left_rook.move_piece((4, 1), list_of_valid_moves)           #move the rook, then exit this if-block for the king to move normally
            elif white_king_has_moved == False:                                      #It is white.
                if selected_piece.board_coordinate in ((7, 8), (3, 8), (5, 8)):        #The King moved to the correct tile (If this is true then it's last tile was the starting tile)
                    if clicked_tile == (7, 8):                 #we clicked on a tile to castle kingside? (We know this move is valid, so castling is allowed)
                        list_of_valid_moves = [(6, 8)]
                        white_right_rook.move_piece((6, 8), list_of_valid_moves)          #move the rook, then exit this if-block for the king to move normally
                    elif clicked_tile == (3, 8):               #we clicked on a tile to castle queenside.
                        list_of_valid_moves = [(4, 8)]
                        white_left_rook.move_piece((4, 8), list_of_valid_moves)           #move the rook, then exit this if-block for the king to move normally

def get_danger_tiles():
    # This function will return two lists, containing the danger tiles for both black and white.
    white_danger_tiles = []
    black_danger_tiles = []
    for piece in list_of_chess_pieces:
        if piece.color == white: # For every white piece on the board.
            if piece.piece_type != pawn:
                # Get the pieces that each and every piece can capture.
                list_of_tiles_where_a_piece_is_allowed_to_go_to = calculate_danger_tiles(piece.piece_type, piece.board_coordinate, piece.color)
            else:
                list_of_tiles_where_a_piece_is_allowed_to_go_to = calculate_danger_tiles(piece.piece_type, piece.board_coordinate, piece.color)
            
            for tile in list_of_tiles_where_a_piece_is_allowed_to_go_to: 
                # Add them to the list of black danger tiles.
                black_danger_tiles.append(tile)

        elif piece.color == black: # For every black piece on the board.
            if piece.piece_type != pawn:
                # Get the pieces that each and every piece can capture.
                list_of_tiles_where_a_piece_is_allowed_to_go_to = calculate_danger_tiles(piece.piece_type, piece.board_coordinate, piece.color)
            else:
                list_of_tiles_where_a_piece_is_allowed_to_go_to = calculate_danger_tiles(piece.piece_type, piece.board_coordinate, piece.color)
            
            for tile in list_of_tiles_where_a_piece_is_allowed_to_go_to:
                # Add them to the list of white danger tiles.
                white_danger_tiles.append(tile)
    return white_danger_tiles, black_danger_tiles

def is_king_in_check(color, danger_tiles):
    king_in_check = False
    if color == black:
        if black_king_piece.board_coordinate in danger_tiles:
            king_in_check = True
    else:
        if white_king_piece.board_coordinate in danger_tiles:
            king_in_check = True
    return king_in_check

#import images
chess_board = pygame.image.load('chess_board.png')

#chessPiece class is where the variables for each piece will be stored
class chessPiece():
    def __init__(self, color:tuple, board_coordinate:tuple, piece_type:str, selected = None, pinned = None):
        if color in (black, white):
            self.color = color
        else:
            raise PieceError
        
        board_coordinate_x, board_coordinate_y = board_coordinate[0], board_coordinate[1]
        self.board_coordinate = (board_coordinate_x, board_coordinate_y)

        piece_x, piece_y = convert_into_pixel_coordinate(board_coordinate_x, board_coordinate_y)
        self.pixel_coordinate = (piece_x, piece_y)

        if piece_type in (pawn, knight, bishop, rook, queen, king):
            self.piece_type = piece_type
        else:
            raise PieceError

        if piece_type == pawn: #Sets the icon
            if color == black:
                self.icon = black_pawn 
            else:
                self.icon = white_pawn
        elif piece_type == knight:
            if color == black:
                self.icon = black_knight
            else:
                self.icon = white_knight
        elif piece_type == bishop:
            if color == black:
                self.icon = black_bishop
            else:
                self.icon = white_bishop
        elif piece_type == rook:
            if color == black:
                self.icon = black_rook
            else:
                self.icon = white_rook
        elif piece_type == queen:
            if color == black:
                self.icon = black_queen
            else:
                self.icon = white_queen
        elif piece_type == king:
            if color == black:
                self.icon = black_king
            else:
                self.icon = white_king

        if selected == None:
            selected = False
        self.selected = selected

        if pinned == None:
            self.pinned = False
            
        list_of_chess_pieces.append(self) #Add the piece to the list_of_chess_pieces list

    def update_icon(self, color:tuple, piece_type:str):
        if piece_type == pawn: #Sets the icon
            if color == black:
                self.icon = black_pawn 
            else:
                self.icon = white_pawn
        elif piece_type == knight:
            if color == black:
                self.icon = black_knight
            else:
                self.icon = white_knight
        elif piece_type == bishop:
            if color == black:
                self.icon = black_bishop
            else:
                self.icon = white_bishop
        elif piece_type == rook:
            if color == black:
                self.icon = black_rook
            else:
                self.icon = white_rook
        elif piece_type == queen:
            if color == black:
                self.icon = black_queen
            else:
                self.icon = white_queen
        elif piece_type == king:
            if color == black:
                self.icon = black_king
            else:
                self.icon = white_king

    def move_piece(self, clicked_tile, list_of_valid_moves):
        if self.piece_type == pawn:
            self.previous_tile = self.board_coordinates

        if clicked_tile in list_of_valid_moves:
            board_coordinate_x, board_coordinate_y = clicked_tile[0], clicked_tile[1]
            self.board_coordinate = clicked_tile

            piece_x, piece_y = convert_into_pixel_coordinate(board_coordinate_x, board_coordinate_y)
            self.pixel_coordinate = (piece_x, piece_y)


    def capture(self, clicked_tile):
        #which piece is there
        for piece in list_of_chess_pieces:
            if piece.board_coordinate == clicked_tile:
                target_piece = piece
        list_of_chess_pieces.remove(target_piece)
        del target_piece #kill the target piece

    # For purposes of simultation. .suspend() .unsuspend()
    # They are used to temporarily remove a piece from the board.
    def freeze(self):
        if self.piece_type != king:
            self.frozen_stats = [self.board_coordinate, self.pixel_coordinate]
            self.board_coordinate = (0, 0) #Out of bounds...
            self.pixel_coordinate = (-50, -50) #Out of bounds...

    def unfreeze(self):
        if self.piece_type != king:
            self.board_coordinate = self.frozen_stats[0]
            self.pixel_coordinate = self.frozen_stats[1]
        
#intialise the main game window
default_surface = pygame.display.set_mode((window_width, window_height))
pygame.display.set_caption("Abdul's Chess")

#create the pieces
#piece_name        = chessPiece(color, (board_coordinates), piece's rank)
white_a_pawn       = chessPiece(white, (a, 7),   pawn)
white_b_pawn       = chessPiece(white, (b, 7),   pawn)
white_c_pawn       = chessPiece(white, (c, 7),   pawn)
white_d_pawn       = chessPiece(white, (d, 7),   pawn)
white_e_pawn       = chessPiece(white, (e, 7),   pawn)
white_f_pawn       = chessPiece(white, (f, 7),   pawn)
white_g_pawn       = chessPiece(white, (g, 7),   pawn)
white_h_pawn       = chessPiece(white, (h, 7),   pawn)
white_left_knight  = chessPiece(white, (b, 8), knight)
white_right_knight = chessPiece(white, (g, 8), knight)
white_left_bishop  = chessPiece(white, (f, 8), bishop)
white_right_bishop = chessPiece(white, (c, 8), bishop)
white_right_rook   = chessPiece(white, (h, 8),   rook)
white_left_rook    = chessPiece(white, (a, 8),   rook)
white_queen_piece  = chessPiece(white, (d, 8),  queen) #white_queen is an icon name, so i named the object white_queen_piece to not mix with the icon variable name.
white_king_piece   = chessPiece(white, (e, 8),   king)

black_a_pawn       = chessPiece(black, (a, 2),   pawn)
black_b_pawn       = chessPiece(black, (b, 2),   pawn)
black_c_pawn       = chessPiece(black, (c, 2),   pawn)
black_d_pawn       = chessPiece(black, (d, 2),   pawn)
black_e_pawn       = chessPiece(black, (e, 2),   pawn)
black_f_pawn       = chessPiece(black, (f, 2),   pawn)
black_g_pawn       = chessPiece(black, (g, 2),   pawn)
black_h_pawn       = chessPiece(black, (h, 2),   pawn)
black_left_knight  = chessPiece(black, (b, 1), knight)
black_right_knight = chessPiece(black, (g, 1), knight)
black_left_bishop  = chessPiece(black, (c, 1), bishop)
black_right_bishop = chessPiece(black, (f, 1), bishop)
black_right_rook   = chessPiece(black, (h, 1),   rook)
black_left_rook    = chessPiece(black, (a, 1),   rook)
black_queen_piece  = chessPiece(black, (d, 1),  queen)
black_king_piece   = chessPiece(black, (e, 1),   king)

def reset_board(list_of_chess_pieces):
    # This function deletes all the chess pieces on the board and creates new ones.
    # It then updates the list of chess pieces.
    for piece in list_of_chess_pieces:
        del piece

    # Rooks need to be passed on to global variables as we will call them during castling outside of this function.

    global white_right_rook, white_left_rook, black_right_rook, black_left_rook
    global white_king_piece, black_king_piece
    list_of_chess_pieces = []
    white_king_has_moved      = False
    black_king_has_moved      = False
    white_king_is_in_check    = False
    black_king_is_in_check    = False

    white_a_pawn       = chessPiece(white, (a, 7),   pawn)
    white_b_pawn       = chessPiece(white, (b, 7),   pawn)
    white_c_pawn       = chessPiece(white, (c, 7),   pawn)
    white_d_pawn       = chessPiece(white, (d, 7),   pawn)
    white_e_pawn       = chessPiece(white, (e, 7),   pawn)
    white_f_pawn       = chessPiece(white, (f, 7),   pawn)
    white_g_pawn       = chessPiece(white, (g, 7),   pawn)
    white_h_pawn       = chessPiece(white, (h, 7),   pawn)
    white_left_knight  = chessPiece(white, (b, 8), knight)
    white_right_knight = chessPiece(white, (g, 8), knight)
    white_left_bishop  = chessPiece(white, (f, 8), bishop)
    white_right_bishop = chessPiece(white, (c, 8), bishop)
    white_right_rook   = chessPiece(white, (h, 8),   rook)
    white_left_rook    = chessPiece(white, (a, 8),   rook)
    white_queen_piece  = chessPiece(white, (d, 8),  queen) #white_queen is an icon name, so i named the object white_queen_piece to not mix with the icon variable name.
    white_king_piece   = chessPiece(white, (e, 8),   king)

    black_a_pawn       = chessPiece(black, (a, 2),   pawn)
    black_b_pawn       = chessPiece(black, (b, 2),   pawn)
    black_c_pawn       = chessPiece(black, (c, 2),   pawn)
    black_d_pawn       = chessPiece(black, (d, 2),   pawn)
    black_e_pawn       = chessPiece(black, (e, 2),   pawn)
    black_f_pawn       = chessPiece(black, (f, 2),   pawn)
    black_g_pawn       = chessPiece(black, (g, 2),   pawn)
    black_h_pawn       = chessPiece(black, (h, 2),   pawn)
    black_left_knight  = chessPiece(black, (b, 1), knight)
    black_right_knight = chessPiece(black, (g, 1), knight)
    black_left_bishop  = chessPiece(black, (c, 1), bishop)
    black_right_bishop = chessPiece(black, (f, 1), bishop)
    black_right_rook   = chessPiece(black, (h, 1),   rook)
    black_left_rook    = chessPiece(black, (a, 1),   rook)
    black_queen_piece  = chessPiece(black, (d, 1),  queen)
    black_king_piece   = chessPiece(black, (e, 1),   king)

    list_of_chess_pieces = [white_a_pawn, white_b_pawn, white_c_pawn, white_d_pawn, white_e_pawn, white_f_pawn, white_g_pawn, white_h_pawn, white_left_knight, white_right_knight, white_left_bishop, white_right_bishop, white_right_rook, white_left_rook, white_queen_piece, white_king_piece, black_a_pawn, black_b_pawn, black_c_pawn, black_d_pawn, black_e_pawn, black_f_pawn, black_g_pawn, black_h_pawn, black_left_knight, black_right_knight, black_left_bishop, black_right_bishop, black_right_rook, black_left_rook, black_queen_piece, black_king_piece]
    
    return list_of_chess_pieces, white_king_has_moved, black_king_has_moved, white_king_is_in_check, black_king_is_in_check

def get_moves_that_would_put_the_king_in_check(piece:chessPiece, white_danger_tiles, black_danger_tiles):
    # This function is called on a specific chess piece and it will return a list of moves that if it takes would put the its own king in check.
    illegal_moves = []
    # A piece is pinned if it is:
    # in a danger tile
    # it moving would put the king into a danger tile.
    if piece.piece_type == king:
        return illegal_moves #Kings can never be pinned.
    

    if piece.color == black:    # If the piece is black
        # Fetch its valid moves.
        list_of_valid_moves, list_of_capturable_pieces, unused = get_theoretical_valid_moves(piece.piece_type, piece.board_coordinate, piece.color, True, white_danger_tiles, black_danger_tiles)
        # For each valid move. Simulate if performing it would put the king in a danger tile.
        for move in list_of_valid_moves:
            # Remember the original position of the piece
            original_tile = piece.board_coordinate
            piece.move_piece(move, list_of_valid_moves) #Move the piece.
            # Recalculate the danger tiles
            unused, black_danger_tiles = get_danger_tiles()
            # If the King is now in check, then that move was illegal.
            if black_king_piece.board_coordinate in black_danger_tiles:
                illegal_moves.append(move)
            # undo the move.
            piece.move_piece(original_tile, [original_tile])

        #Repeat the same simulation but for captures.
        for move in list_of_capturable_pieces:
            # Remember the original position of the piece
            original_tile = piece.board_coordinate
            # Identify the piece that's about to freeze.
            for target_piece in list_of_chess_pieces:
                if target_piece.board_coordinate == move and target_piece.piece_type != king:
                    # Freeze the piece and move our new piece there
                    target_piece.freeze()
                    piece.move_piece(move, [move])
                    # Recalculate the danger tiles
                    unused, black_danger_tiles = get_danger_tiles()
                    # If the King is now in check, then that move was illegal.
                    if black_king_piece.board_coordinate in black_danger_tiles:
                        illegal_moves.append(move) # as the loop continues illegal_moves will accumulate more and more tiles.
                    # undo the move and unfreeze the dead piece.
                    target_piece.unfreeze()
                    piece.move_piece(original_tile, [original_tile])

    else:   # The piece is white.
        # Fetch its valid moves.
        list_of_valid_moves, list_of_capturable_pieces, unused = get_theoretical_valid_moves(piece.piece_type, piece.board_coordinate, piece.color, True, white_danger_tiles, black_danger_tiles)
        # For each valid move. Simulate if performing it would put the king in a danger tile.
        for move in list_of_valid_moves:
            # Remember the original position of the piece
            original_tile = piece.board_coordinate
            piece.move_piece(move, list_of_valid_moves) #Move the piece.
            # Recalculate the danger tiles
            white_danger_tiles, unused = get_danger_tiles()
            # If the King is now in check, then that move was illegal.
            if white_king_piece.board_coordinate in white_danger_tiles:
                illegal_moves.append(move)
            # undo the move.
            piece.move_piece(original_tile, [original_tile])

        #Repeat the same simulation but for captures.
        for move in list_of_capturable_pieces:
            # Remember the original position of the piece
            original_tile = piece.board_coordinate
            # Identify the piece that's about to freeze.
            for target_piece in list_of_chess_pieces:
                if target_piece.board_coordinate == move:
                    # Freeze the piece and move our new piece there
                    target_piece.freeze()
                    piece.move_piece(move, [move])
                    # Recalculate the danger tiles
                    white_danger_tiles, unused = get_danger_tiles()
                    # If the King is now in check, then that move was illegal.
                    if white_king_piece.board_coordinate in white_danger_tiles:
                        illegal_moves.append(move) # as the loop continues illegal_moves wiill accumulate more and more tiles.
                    # undo the move and unfreeze the dead piece.
                    target_piece.unfreeze()
                    piece.move_piece(original_tile, [original_tile])

    return illegal_moves

def check_for_check_mate(list_of_chess_pieces, white_king_is_in_check, black_king_is_in_check, white_danger_tiles, black_danger_tiles):
    # You are in check mate if there is no move that can put you out of check.

    # Simulate every move for every piece,
    # add the ones that do not leave you in check into the legal_moves list
    # if that list is empty then you have lost.
    white_legal_moves = []
    black_legal_moves = []
    black_in_check_mate = False
    white_in_check_mate = False

    for piece in list_of_chess_pieces:
        if piece.color == white:
            list_of_valid_moves, list_of_capturable_pieces, unused = get_valid_moves(piece.piece_type, piece.board_coordinate, piece.color, True, white_danger_tiles, black_danger_tiles, piece, False)
            # For each valid move. Simulate if performing it would put the king in check
            for move in list_of_valid_moves:
                # Remember the original position of the piece
                original_tile = piece.board_coordinate
                piece.move_piece(move, list_of_valid_moves) #Move the piece.
                # Recalculate the danger tiles
                white_danger_tiles, unused = get_danger_tiles()
                # If the King is now in check, then that move was illegal.
                if white_king_piece.board_coordinate not in white_danger_tiles:
                    white_legal_moves.append(move) # If that move won't put the king in check, then add it to legal_moves list.
                # undo the move.
                piece.move_piece(original_tile, [original_tile])
            # Repeat this simulation for the captures.
            for move in list_of_capturable_pieces:
                # Remember the original position of the piece
                original_tile = piece.board_coordinate
                # Identify the piece that's about to freeze.
                for target_piece in list_of_chess_pieces:
                    if target_piece.board_coordinate == move:
                        target_piece = piece
                # Freeze the piece and move our new piece there
                target_piece.freeze()
                piece.move_piece(move, [move])
                # Recalculate the danger tiles
                white_danger_tiles, unused = get_danger_tiles()
                # If the King is now in check, then that move was illegal.
                if white_king_piece.board_coordinate not in white_danger_tiles:
                    white_legal_moves.append(move) # If that move won't put the king in check, then add it to legal_moves list.
                # undo the move and unfreeze the dead piece.
                target_piece.unfreeze()
                piece.move_piece(original_tile, [original_tile])
        elif piece.color == black:
            # Fetch its valid moves.
            list_of_valid_moves, list_of_capturable_pieces, unused = get_valid_moves(piece.piece_type, piece.board_coordinate, piece.color, True, white_danger_tiles, black_danger_tiles, piece, False)
            # For each valid move. Simulate if performing it would put the king in a danger tile.
            for move in list_of_valid_moves:
                # Remember the original position of the piece
                original_tile = piece.board_coordinate
                piece.move_piece(move, list_of_valid_moves) #Move the piece.
                # Recalculate the danger tiles
                unused, black_danger_tiles = get_danger_tiles()
                # If the King is now in check, then that move was illegal.
                if black_king_piece.board_coordinate not in black_danger_tiles:
                    black_legal_moves.append(move)
                # undo the move.
                piece.move_piece(original_tile, [original_tile])

            #Repeat the same simulation but for captures.
            for move in list_of_capturable_pieces:
                # Remember the original position of the piece
                original_tile = piece.board_coordinate
                # Identify the piece that's about to freeze.
                for target_piece in list_of_chess_pieces:
                    if target_piece.board_coordinate == move:
                        target_piece = piece
                # Freeze the piece and move our new piece there
                target_piece.freeze()
                piece.move_piece(move, [move])
                # Recalculate the danger tiles
                unused, black_danger_tiles = get_danger_tiles()
                # If the King is now in check, then that move was illegal.
                if black_king_piece.board_coordinate not in black_danger_tiles:
                    black_legal_moves.append(move) # as the loop continues illegal_moves wiill accumulate more and more tiles.
                # undo the move and unfreeze the dead piece.
                target_piece.unfreeze()
                piece.move_piece(original_tile, [original_tile])

    # If legal_moves is empty and the player is in check, then the player has lost.    
    # If legal_moves is empty and the player is not in check, then return 'draw'.    
    if len(white_legal_moves) == 0:
        if white_king_piece.board_coordinate in white_danger_tiles:
            white_in_check_mate = True
        else:
            return 'draw', 'draw'
    if len(black_legal_moves) == 0:
        if black_king_piece.board_coordinate in black_danger_tiles:
            black_in_check_mate = True
        else:
            return 'draw', 'draw'

    return white_in_check_mate, black_in_check_mate

#Text processing
font_object          = pygame.font.Font('freesansbold.ttf', 30)
reset_text           = font_object.render('Reset board', True, white, dark_grey)
reset_button_Rect    = reset_text.get_rect()
one_move_button_text = font_object.render('One move', True, white, dark_grey)
one_move_button_Rect = one_move_button_text.get_rect()

white_victory_text         = font_object.render('Checkmate! White wins!', True, white, dark_grey)
white_victory_text_Rect    = white_victory_text.get_rect()

black_victory_text         = font_object.render('Checkmate! Black wins!', True, white, dark_grey)
black_victory_text_Rect    = black_victory_text.get_rect()

stalemate_text             = font_object.render("Stalemate! It's a Draw!", True, white, dark_grey)
stalemate_text_Rect        = stalemate_text.get_rect()

one_move_button_Rect.centerx = one_move_button_x + 0.5 * one_move_button_width
one_move_button_Rect.centery = one_move_button_y + 0.5 * one_move_button_height
reset_button_Rect.centerx = reset_button_x + 0.5 * reset_button_width
reset_button_Rect.centery = reset_button_y + 0.5 * reset_button_height
black_victory_text_Rect.centerx = victory_button_x +  victory_button_width / 2
black_victory_text_Rect.centery = victory_button_y + victory_button_height / 2
white_victory_text_Rect.centerx = victory_button_x +  victory_button_width / 2
white_victory_text_Rect.centery = victory_button_y + victory_button_height / 2
stalemate_text_Rect.centerx = victory_button_x +  victory_button_width / 2
stalemate_text_Rect.centery = victory_button_y + victory_button_height / 2

while True: #main loop
    default_surface.fill(dark_theme)
    default_surface.blit(chess_board, (board_x, board_y)) # draw the board

    # Check if anyone is in checkmate
    white_in_check_mate, black_in_check_mate = check_for_check_mate(list_of_chess_pieces, white_king_is_in_check, black_king_is_in_check, white_danger_tiles, black_danger_tiles)
    white_victory_button_object = pygame.Rect(victory_button_x, victory_button_y, victory_button_width, victory_button_height)
    black_victory_button_object = pygame.Rect(victory_button_x, victory_button_y, victory_button_width, victory_button_height)

    #Check if the Kings are in check, if they are flash the tile to warn the player.
    white_king_in_check = is_king_in_check(white, white_danger_tiles)
    black_king_in_check = is_king_in_check(black, black_danger_tiles)

    flash_counter += 1 # Timing for the flashing of the highlight for when the king is in check.
    if flash_counter > 10: 
        flash_counter = 0

    if flash_counter > 5: #Keep count of how long to wait before flashing.
        if white_king_in_check == True:
            highlight_tile(white_king_piece.pixel_coordinate, None, red)
        if black_king_in_check == True:
            highlight_tile(black_king_piece.pixel_coordinate, None, red)


    #Update whose turn it is.
    one_move_per_turn = next_one_move_per_turn
    current_turn = next_turn

    #Draw a buttton that when clicked will toggle whether the player is forced into making one move per turn.
    one_move_button_object = pygame.Rect(one_move_button_x, one_move_button_y, one_move_button_width, one_move_button_height)
    if one_move_per_turn == True:
        one_move_button_text = font_object.render('One move', True, black, yellow)
        pygame.draw.rect(default_surface, yellow, one_move_button_object)
    else:
        one_move_button_text = font_object.render('One move', True, white, dark_grey)
        pygame.draw.rect(default_surface, dark_grey, one_move_button_object)
    one_move_button_Rect = one_move_button_text.get_rect()
    one_move_button_Rect.centerx = one_move_button_x + 0.5 * one_move_button_width
    one_move_button_Rect.centery = one_move_button_y + 0.5 * one_move_button_height
    default_surface.blit(one_move_button_text, one_move_button_Rect) 

    #Draw a button that when clicked will reset the board to its original state.
    reset_button_object = pygame.Rect(reset_button_x, reset_button_y, reset_button_width, reset_button_height)
    pygame.draw.rect(default_surface, dark_grey, reset_button_object)
    default_surface.blit(reset_text, reset_button_Rect)

    #Any pawns to promote?
    for piece in list_of_chess_pieces:
        piece.piece_type = change_piece(piece.piece_type, piece.board_coordinate, piece.color, queen)
        piece.update_icon(piece.color, piece.piece_type)

    #Update the list_of_valid_moves
    try:
        list_of_valid_moves, list_of_capturable_pieces, list_of_valid_enpassants = get_valid_moves(selected_piece.piece_type, selected_piece.board_coordinate, selected_piece.color, a_piece_is_selected, white_danger_tiles, black_danger_tiles, selected_piece)
    except NameError: #No selected piece? Not the end of the world, keep going
        list_of_valid_moves = []

    #check if the mouse is over a tile, if it is then highlight it
    is_mouse_over_a_tile(mouse_x, mouse_y)

    #check if a piece is selected
    if a_piece_is_selected == True:
        list_of_valid_moves, list_of_capturable_pieces, list_of_valid_enpassants = get_valid_moves(selected_piece.piece_type, selected_piece.board_coordinate, selected_piece.color, a_piece_is_selected, white_danger_tiles, black_danger_tiles, selected_piece)
        for tile in list_of_valid_moves:
            highlight_tile(convert_into_pixel_coordinate(*tile))
    
    for piece in list_of_chess_pieces:#for each piece on the board
        if piece.selected == True: #highlight it in yellow if it is selected.
            highlight_tile(piece.pixel_coordinate, None, yellow) #Highlight function does not need unpacking of the coordinate tuple! It accepts both a tuple of 2 variables or 2 unpacked variables
        default_surface.blit(piece.icon, (piece.pixel_coordinate))#draw the piece

    # If someone has won then draw a box to inform the players.
    if black_in_check_mate == 'draw' or white_in_check_mate == 'draw':
        stalemate_object = pygame.Rect(victory_button_x, victory_button_y, victory_button_width, victory_button_height)
        pygame.draw.rect(default_surface, dark_grey, stalemate_object)
        default_surface.blit(stalemate_text, stalemate_text_Rect)

    if black_in_check_mate == True:
        pygame.draw.rect(default_surface, dark_grey, white_victory_button_object)
        default_surface.blit(white_victory_text, white_victory_text_Rect)
    if white_in_check_mate == True:
        pygame.draw.rect(default_surface, dark_grey, black_victory_button_object)
        default_surface.blit(black_victory_text, black_victory_text_Rect)
    #Update the danger_tiles
    white_danger_tiles, black_danger_tiles = get_danger_tiles()


    #Update the display and then wait until it's time to draw the next frame
    pygame.display.update()
    fps_clock.tick(FPS) #Locks the game to 30 FPS

    for event in pygame.event.get(): #event_handling_loop
        if event.type == QUIT:
                pygame.quit()
                sys.exit()
        elif event.type == MOUSEMOTION:
            mouse_x, mouse_y = event.pos
        elif event.type == MOUSEBUTTONUP:
            
            #check if the reset button is clicked.
            if mouse_x > reset_button_x and mouse_x < window_width - reset_button_gap and mouse_y > reset_button_y and mouse_y < window_height - reset_button_gap:
                list_of_chess_pieces, white_king_has_moved, black_king_has_moved, white_king_is_in_check, black_king_is_in_check = reset_board(list_of_chess_pieces)
                #ensure all pieces are deselected.
                a_piece_is_selected = False
                for piece in list_of_chess_pieces:
                    piece.selected = False

                next_turn = white
            if mouse_x > one_move_button_x and mouse_x < (one_move_button_x + one_move_button_width) and mouse_y > one_move_button_y and mouse_y < (one_move_button_y + one_move_button_height):
                if one_move_per_turn == True:
                    next_one_move_per_turn = False
                else:
                    next_one_move_per_turn = True
                

            try: #update the list_of valid moves. Just in case
                list_of_valid_moves, list_of_capturable_pieces, list_of_valid_enpassants = get_valid_moves(selected_piece.piece_type, selected_piece.board_coordinate, selected_piece.color, a_piece_is_selected, white_danger_tiles, black_danger_tiles, selected_piece)
            except NameError: #No selected piece? Not the end of the world, keep going
                list_of_valid_moves = []

            mouse_over_tile = is_mouse_over_a_tile(mouse_x, mouse_y)
            clicked_tile = get_highlighted_tile(mouse_x, mouse_y)
            
            for piece in list_of_chess_pieces:
                if piece.selected == True:
                    a_piece_is_selected = True
                    selected_piece = piece
                if mouse_over_tile == True: #Mouse over tile?
                    for piece in list_of_chess_pieces:
                        selected_board_x, selected_board_y = convert_into_board_coordinate(mouse_x, mouse_y)
                        selected_board_coordinates = (selected_board_x, selected_board_y)
                        if piece.board_coordinate == selected_board_coordinates: #Piece is there?
                            if piece.selected == False: #... and it isn't selected
                                if a_piece_is_selected == False: #... and no other piece on the board is selected
                                    if one_move_per_turn == True and current_turn == piece.color: #And it is that player's turn.
                                        piece.selected = True
                                    if one_move_per_turn == False: # If one move per turn is False, then don't check whose turn it is.
                                        piece.selected = True
                                else: #another piece is selected. deselect it and then select the new piece
                                    if one_move_per_turn == True and current_turn == piece.color:
                                        selected_piece.selected = False
                                        piece.selected = True
                                        a_piece_is_selected = True
                                        selected_piece = piece

                                        #Update the selected_piece
                                        for piece in list_of_chess_pieces:
                                            if piece.selected == True:
                                                a_piece_is_selected = True
                                                selected_piece = piece
                                    if one_move_per_turn == False:
                                        # If it isnt in the capture tiles. then deselect selected_piece and select it
                                        if clicked_tile not in (list_of_capturable_pieces):
                                            selected_piece.selected = False
                                            piece.selected = True
                                            a_piece_is_selected = True
                                            selected_piece = piece

                                            #Update the selected_piece
                                            for piece in list_of_chess_pieces:
                                                if piece.selected == True:
                                                    a_piece_is_selected = True
                                                    selected_piece = piece

                    if clicked_tile in list_of_capturable_pieces and a_piece_is_selected == True: #Are we allowed to capture it?
                        if clicked_tile in list_of_valid_enpassants:
                            # for enpassant we have to kill the tile infront of the clicked tile.
                            if selected_piece.color == black:
                                en_passant_tile = (clicked_tile[0], (clicked_tile[1] - 1))
                            else:
                                en_passant_tile = (clicked_tile[0], (clicked_tile[1] + 1))

                            selected_piece.capture(en_passant_tile)    
                        else:
                            selected_piece.capture(clicked_tile)

                        try:
                           list_of_valid_moves, list_of_capturable_pieces, list_of_valid_enpassants = get_valid_moves(selected_piece.piece_type, selected_piece.board_coordinate, selected_piece.color, a_piece_is_selected, white_danger_tiles, black_danger_tiles, selected_piece)
                        except NameError: #No selected piece? Not the end of the world, keep going
                           list_of_valid_moves = [clicked_tile]

                        if selected_piece.piece_type == pawn:
                            list_of_valid_moves = [clicked_tile]

                        selected_piece.move_piece(clicked_tile, list_of_valid_moves)
                        selected_piece.selected = False
                        a_piece_is_selected = False

                        if current_turn == white: #Alternate between whose turn it is every move.
                            next_turn = black
                        else:
                            next_turn = white
    
                    elif clicked_tile in list_of_valid_moves: #Are we clicking on a valid move tile?
                        #YES WE ARE!! time to move a piece!
                        #check if we are castling
                        castle(clicked_tile, selected_piece, list_of_valid_moves, white_king_has_moved, black_king_has_moved)
                        selected_piece.move_piece(clicked_tile, list_of_valid_moves)
                        selected_piece.selected = False
                        a_piece_is_selected = False

                        if selected_piece.piece_type == king:
                            if selected_piece.color == black:
                                black_king_has_moved = True
                            else:
                                white_king_has_moved = True

                        if current_turn == white: #Alternate between whose turn it is every move.
                            next_turn = black
                        else:
                            next_turn = white

# End