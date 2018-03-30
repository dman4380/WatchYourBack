# functions which perform the massacre action

from board import Board
from team import Team
from piece import Piece

state_previous = Board()

def find_elimination(g_board,t_attack,t_defend,depth,best_depth):
    # find the nearest elimination
    dir_check = [[0,1],[-1,0],[0,-1],[1,0]]
    ally_begin = t_attack.pieces_count()
    enemy_begin = t_defend.pieces_count()
    if depth <= 0 or best_depth >= depth:
        return 0
    state_set = []
    best_state = 0
    do_return = False
    for p in t_attack.get_my_pieces():
        if p.distance_nearest(t_defend.get_my_pieces()) > depth:
            continue
        for d in dir_check:
            new_pos = [-1,-1]
            p_pos = p.get_position()
            if g_board.piece_can_move(p,d[0],d[1]):
                new_pos = [p_pos[0]+d[0],p_pos[1]+d[1]]
            elif g_board.piece_can_move(p,d[0]*2,d[1]*2):
                new_pos = [p_pos[0]+d[0]*2,p_pos[1]+d[1]*2]
            if not g_board.position_out_of_bounds(new_pos[0],new_pos[1]):
                n_board = Board()
                n_attack = Team(t_attack.colour,n_board,False)
                n_defend = Team(t_defend.colour,n_board,False)
                for c in g_board.pieces:
                    if c != p:
                        n_board.add_piece(c.colour,c.row,c.column)
                    else:
                        n_board.add_piece(p.colour,new_pos[0],new_pos[1])
                n_board.pieces_eliminate(t_attack.colour)
                n_state = [n_board,n_attack,n_defend,p,d]
                state_set.append(n_state)
                ally_end = n_attack.pieces_count()
                enemy_end = n_defend.pieces_count()
                n_score = ally_end - ally_begin
                n_score += enemy_begin - enemy_end
                if n_score > 0:
                    return [p,d,depth]
        for s in state_set:
            check_state = 0
            if best_state == 0:
                check_state = find_elimination(s[0],s[1],s[2],depth-1,0)
            elif best_state[2] < depth:
                check_state = find_elimination(s[0],s[1],s[2],
                    depth-1,best_state[2])
            if check_state != 0:
                if best_state == 0:
                    best_state = [s[3],s[4],check_state[2]]
                elif check_state[2] > best_state[2]:
                    best_state = [s[3],s[4],check_state[2]]
            state_set.remove(s)
            if best_state != 0:
                if best_state[2] >= depth:
                    break
                    do_return = True
        if do_return:
            break
    return best_state


def massacre(g_board,t_attack,t_defend):
    # TODO: massacre function
    # directions to check for adjacent pieces, movement, etc.
    dir_check = [[0,1],[-1,0],[0,-1],[1,0]]
    # try to find positions to move to which surround an enemy
    s_max = -1000
    p_move = 0
    d_move = [0,0]
    ally_begin = t_attack.pieces_count()
    enemy_begin = t_defend.pieces_count()
    depth_limit = 2
    ally_pieces = t_attack.get_my_pieces()
    enemy_pieces = t_defend.get_my_pieces()
    move = find_elimination(g_board,t_attack,t_defend,depth_limit,0)
    if move == 0:
        # fail-safe if the search function cannot find an elimination sequence
        # try moving a piece towards an enemy
        # have all pieces attempt to enclose ONE enemy
        dist = 1000
        e = enemy_pieces[0] # wouldn't be called if no enemy pieces
        for p in ally_pieces:
            e_pos = e.get_position()
            p_pos = p.get_position()
            for d in dir_check:
                n_pos = [-1,-1]
                if g_board.piece_can_move(p,d[0],d[1]):
                    n_pos = [p_pos[0]+d[0],p_pos[1]+d[1]]
                elif g_board.piece_can_move(p,d[0]*2,d[1]*2):
                    n_pos = [p_pos[0]+d[0]*2,p_pos[1]+d[1]*2]
                if not g_board.position_out_of_bounds(n_pos[0],n_pos[1]):
                    d_current = abs(e_pos[0]-p_pos[0])
                    d_current += abs(e_pos[1]-p_pos[1])
                    d_new = abs(e_pos[0]-n_pos[0])
                    d_new += abs(e_pos[1]-n_pos[1])
                    if p_move == 0:
                        # select as a 'default' move to make
                        p_move = p
                        d_move = d
                        if d_new < d_current:
                            dist = d_current
                    elif (d_current < dist and d_new < d_current
                            and d_current > depth_limit):
                        # movement of distant piece towards
                        # a non-adjacent enemy outside the depth_limit
                        p_move = p
                        d_move = d
                        dist = d_current
    else:
        p_move = move[0]
        d_move = move[1]
    if type(p_move) != Piece:
        return False # failure, couldn't find a moveable piece
    str_out = '(' + str(p_move.row) + ', ' + str(p_move.column) + ')'
    pos = p_move.get_position()
    if g_board.piece_can_move(p_move,d_move[0],d_move[1]):
        p_move.set_position(pos[0]+d_move[0],pos[1]+d_move[1])
    elif g_board.piece_can_move(p_move,d_move[0]*2,d_move[1]*2):
        p_move.set_position(pos[0]+d_move[0]*2,pos[1]+d_move[1]*2)
    g_board.pieces_eliminate(t_attack.colour)
    str_out += ' -> '
    str_out += '(' + str(p_move.row) + ', ' + str(p_move.column) + ')'
    print(str_out)
    return True # managed to move a piece
