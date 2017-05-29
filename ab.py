INF = float('inf')


def minimax(node, depth=2):
    return alphabeta(node, depth, -INF, INF, True)


def alphabeta(node, depth, alpha, beta, isMaximizing):
    if depth == 0 or node.is_terminating():
        return node.value()
    if isMaximizing:  # maximizing player, "our guy"
        v = -INF
        for child in node.children():
            v = max(v, alphabeta(child, depth - 1, alpha, beta, False))
            alpha = max(alpha, v)
            if beta <= alpha:
                break
        return v
    else:
        v = INF
        for child in node.children():
            v = min(v, alphabeta(child, depth - 1, alpha, beta, True))
            beta = min(beta, v)
            if beta <= alpha:
                break
        return v
