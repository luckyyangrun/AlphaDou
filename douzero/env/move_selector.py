import collections

# 全局癞子牌数值
WILD_RANK = None

def set_wild_rank(wild):
    global WILD_RANK
    WILD_RANK = wild

def effective_rank(move):
    """
    计算动作的有效牌值：如果存在自然牌则返回其中最小的自然牌值，否则返回 WILD_RANK。
    """
    natural = [card for card in move if card != WILD_RANK]
    if natural:
        return min(natural)
    else:
        return WILD_RANK

def common_handle(moves, rival_move):
    new_moves = []
    rival_eff = effective_rank(rival_move)
    for move in moves:
        if effective_rank(move) > rival_eff:
            new_moves.append(move)
    return new_moves

def filter_type_1_single(moves, rival_move):
    return common_handle(moves, rival_move)

def filter_type_2_pair(moves, rival_move):
    return common_handle(moves, rival_move)

def filter_type_3_triple(moves, rival_move):
    return common_handle(moves, rival_move)

def filter_type_4_bomb(moves, rival_move):
    return common_handle(moves, rival_move)

# King bomb 无需筛选

def filter_type_6_3_1(moves, rival_move):
    rival_eff = effective_rank(rival_move)
    new_moves = []
    for move in moves:
        if effective_rank(move) > rival_eff:
            new_moves.append(move)
    return new_moves

def filter_type_7_3_2(moves, rival_move):
    rival_eff = effective_rank(rival_move)
    new_moves = []
    for move in moves:
        if effective_rank(move) > rival_eff:
            new_moves.append(move)
    return new_moves

def filter_type_8_serial_single(moves, rival_move):
    return common_handle(moves, rival_move)

def filter_type_9_serial_pair(moves, rival_move):
    return common_handle(moves, rival_move)

def filter_type_10_serial_triple(moves, rival_move):
    return common_handle(moves, rival_move)

def filter_type_11_serial_3_1(moves, rival_move):
    rival_counter = collections.Counter(rival_move)
    # 取 triple 部分的最高自然牌
    rival_eff = max([k for k, v in rival_counter.items() if v >= 3] or [effective_rank(rival_move)])
    new_moves = []
    for move in moves:
        move_counter = collections.Counter(move)
        my_eff = max([k for k, v in move_counter.items() if v >= 3] or [effective_rank(move)])
        if my_eff > rival_eff:
            new_moves.append(move)
    return new_moves

def filter_type_12_serial_3_2(moves, rival_move):
    rival_counter = collections.Counter(rival_move)
    rival_eff = max([k for k, v in rival_counter.items() if v >= 3] or [effective_rank(rival_move)])
    new_moves = []
    for move in moves:
        move_counter = collections.Counter(move)
        my_eff = max([k for k, v in move_counter.items() if v >= 3] or [effective_rank(move)])
        if my_eff > rival_eff:
            new_moves.append(move)
    return new_moves

def filter_type_13_4_2(moves, rival_move):
    rival_eff = effective_rank(rival_move)
    new_moves = []
    for move in moves:
        if effective_rank(move) > rival_eff:
            new_moves.append(move)
    return new_moves

def filter_type_14_4_22(moves, rival_move):
    rival_counter = collections.Counter(rival_move)
    rival_eff = 0
    for k, v in rival_counter.items():
        if v == 4 and k != WILD_RANK:
            rival_eff = max(rival_eff, k)
    new_moves = []
    for move in moves:
        move_counter = collections.Counter(move)
        my_eff = 0
        for k, v in move_counter.items():
            if v == 4 and k != WILD_RANK:
                my_eff = max(my_eff, k)
        if my_eff > rival_eff:
            new_moves.append(move)
    return new_moves
