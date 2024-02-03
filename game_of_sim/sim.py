from typing import List, Dict, Set

class Sim:
    def __init__(self):
        self.__onMove = 1
        self.__finished = False
        self.__edge_labels = []
        self.__R, self.__RvB, self.__B, self.__moves = [], [], [], []
        self.__edge_colors = {}  # 0 not colored yet, 1 red, 2 blue
        self.__move10, self.__move12 = "", ""
        self.use_engine = True
        self.reset()

    def __normalize_edge(self, edge):
        if len(edge) != 2 or edge[0] == edge[1] or edge[0] < 'A' or edge[0] > 'F' or edge[1] < 'A' or edge[1] > 'F':
            raise ValueError("Invalid edge label")
        if edge[0] > edge[1]:
            edge = edge[1] + edge[0]
        return edge

    def __make_edge(self, P, Q):
        ans = P + Q
        return self.__normalize_edge(ans)

    def edge_from_vertex(self, PQ, P):
        return PQ[0] == P or PQ[1] == P

    def __common_vertex(self, PQ, PR):
        if PQ[0] == PR[0]:
            return PQ[0]
        if PQ[0] == PR[1]:
            return PQ[0]
        if PQ[1] == PR[0]:
            return PQ[1]
        if PQ[1] == PR[1]:
            return PQ[1]
        raise ValueError("Invalid labels")

    def __check_game_finished(self):
        for PQ in self.__edge_labels:
            if self.__edge_colors[PQ] == 0:
                continue
            color_PQ = self.get_edge_color(PQ)
            for R in 'ABCDEF':
                if R == PQ[0] or R == PQ[1]:
                    continue
                PR = self.__make_edge(PQ[0], R)
                QR = self.__make_edge(PQ[1], R)
                if self.get_edge_color(PR) == color_PQ and self.get_edge_color(QR) == color_PQ:
                    self.__finished = True
                    return self.__finished
        return self.__finished

    def __is_playable(self, PQ, color):
        if self.__edge_colors[PQ]:
            return False
        for R in 'ABCDEF':
            if R == PQ[0] or R == PQ[1]:
                continue
            PR = self.__make_edge(PQ[0], R)
            QR = self.__make_edge(PQ[1], R)
            if self.get_edge_color(PR) == color and self.get_edge_color(QR) == color:
                return False
        return True

    def __compute_playable_edges(self):
        self.__R.clear()
        self.__B.clear()
        self.__RvB.clear()
        for PQ in self.__edge_labels:
            if self.__edge_colors[PQ] > 0:
                continue
            red_playable = self.__is_playable(PQ, 1)
            blue_playable = self.__is_playable(PQ, 2)
            if red_playable:
                if blue_playable:
                    self.__RvB.append(PQ)
                else:
                    self.__R.append(PQ)
            elif blue_playable:
                self.__B.append(PQ)

    def __compute_min_x(self):
        Xs = {}
        for QS in self.__RvB:
            self.__edge_colors[QS] = 2
            Xs[QS] = 0
            for PQ in self.__RvB:
                if PQ != QS and not self.__is_playable(PQ, 2):
                    Xs[QS] += 1  # PQ is lost upon playing on QS
            for PQ in self.__B:
                if PQ != QS and not self.__is_playable(PQ, 2):
                    Xs[QS] += 1  # PQ is lost upon playing on QS
            self.__edge_colors[QS] = 0
        X = sorted(Xs.items(), key=lambda x: x[1])
        min_x_val = X[0][1]
        ans = [edge for edge, val in X if val == min_x_val]
        return ans

    def __compute_z(self, ij):
        ans = 0
        for k in 'ABCDEF':
            if k == ij[0] or k == ij[1]:
                continue
            ik = self.__make_edge(ij[0], k)
            jk = self.__make_edge(ij[1], k)
            if self.__is_playable(ik, 2) and self.__is_playable(jk, 2):
                ans += 2
            elif self.__edge_colors[ik] == 1 and self.__is_playable(jk, 1):
                ans += 1
            elif self.__edge_colors[jk] == 1 and self.__is_playable(ik, 1):
                ans += 1
        return ans

    def __get_best_move(self):
        self.__compute_playable_edges()
        Xs = self.__compute_min_x()
        if len(Xs) == 1:
            return Xs[0]
        Zs = [(self.__compute_z(ij), ij) for ij in Xs]
        Zs.sort()
        return Zs[0][1]

    def reset(self):
        self.__onMove = 1
        self.__moves.clear()
        self.__finished = False
        if not self.__edge_labels:
            for P in 'ABCDEF':
                for Q in 'ABCDEF':
                    if P < Q:
                        self.__edge_labels.append(self.__make_edge(P, Q))
        self.__edge_colors.clear()
        for label in self.__edge_labels:
            self.__edge_colors[label] = 0

    def play(self, PQ):
        PQ = self.__normalize_edge(PQ)
        if self.__finished:
            return
            raise ValueError("The game has been finished")
        if self.get_edge_color(PQ) > 0:
            return
            raise ValueError("This move is already played")
        self.__moves.append(PQ)
        self.__edge_colors[PQ] = 2 - (self.__onMove % 2)
        self.__onMove += 1
        self.__check_game_finished()

        if not self.__finished and self.use_engine and self.is_blue_turn():
            if self.__onMove == 2:
                for R in 'ABCDEF':
                    if R != PQ[0] and R != PQ[1]:
                        self.play(self.__make_edge(PQ[0], R))
                        return
            elif self.__onMove == 4:
                st = set()
                for edge in self.__moves:
                    st.add(edge[0])
                    st.add(edge[1])
                if len(st) == 3:
                    PR = self.__moves[0]
                    P = self.__common_vertex(PR, PQ)
                    for i in range(len(self.__edge_labels) - 1, -1, -1):
                        if not self.__edge_colors[self.__edge_labels[i]] and self.edge_from_vertex(self.__edge_labels[i], P):
                            self.play(self.__edge_labels[i])
                            return
                else:
                    V = self.__common_vertex(self.__moves[0], self.__moves[1])
                    R = self.__moves[0][0] if self.__moves[0][0] != V else self.__moves[0][1]
                    S = self.__moves[1][0] if self.__moves[1][0] != V else self.__moves[1][1]
                    self.play(self.__make_edge(R, S))
                    return
            elif self.__onMove == 6 or self.__onMove == 8:
                best_move = self.__get_best_move()
                self.play(best_move)
                return
            elif self.__onMove == 10:
                self.__move10, self.__move12 = "", ""
                self.__compute_playable_edges()
                if len(self.__R) == 1 and len(self.__RvB) == 2 and len(self.__B) == 3:
                    for side1 in self.__RvB:
                        self.__edge_colors[side1] = 2
                        for side2 in self.__B:
                            if self.__is_playable(side2, 2):
                                self.__edge_colors[side2] = 2
                                for side3 in self.__B:
                                    if side3 != side2 and self.__is_playable(side3, 2):
                                        self.__move10 = side1
                                        self.__move12 = side2
                                        break
                                self.__edge_colors[side2] = 0
                        self.__edge_colors[side1] = 0
                    self.play(self.__move10)
                    return
                elif len(self.__R) == 1 and len(self.__RvB) == 3 and len(self.__B) == 2: # Rule 5: "AF", "AB", "BF", "EF", "CD", "CF", "BE", "AE", "DF"
                    for side1 in self.__RvB:
                        self.__edge_colors[side1] = 2
                        rule5_best_move = True
                        for side2 in self.__RvB:
                            if side1 == side2:
                                continue
                            if not self.__is_playable(side2, 2):
                                rule5_best_move = False
                                break
                        self.__edge_colors[side1] = 0
                        if rule5_best_move:
                            self.play(side1)
                            return
                    raise ValueError(f"Strategy not found on move {self.__onMove}")
                else:
                    best_move = self.__get_best_move()
                    self.play(best_move)
                    return
            elif self.__onMove == 12:
                if self.__move12 != "":
                    self.play(self.__move12)
                else:
                    self.__compute_playable_edges()
                    if self.__RvB:
                        self.play(self.__RvB[0])
                    elif self.__B:
                        self.play(self.__B[0])
                    else:
                        raise ValueError(f"Strategy not found on move {self.__onMove}")
                return
            elif self.__onMove == 14:
                self.__compute_playable_edges()
                if self.__RvB:
                    self.play(self.__RvB[0])
                elif self.__B:
                    self.play(self.__B[0])
                else:
                    raise ValueError(f"Strategy not found on move {self.__onMove}")

    def get_moves(self):
        return self.__moves

    def get_next_move(self):
        return self.__onMove

    def is_red_turn(self):
        return self.__onMove % 2 == 1

    def is_blue_turn(self):
        return self.__onMove % 2 == 0

    def is_finished(self):
        return self.__finished

    def get_all_edge_labels(self):
        return self.__edge_labels

    def get_edge_color(self, edge):
        edge = self.__normalize_edge(edge)
        return self.__edge_colors[edge]

    def get_line_color(self, P, Q):
        edge = self.__make_edge(P, Q)
        return self.get_edge_color(edge)

    def get_triangle_edges(self):
        if not self.__finished:
            return []
        for P in 'ABCDEF':
            for Q in 'ABCDEF':
                if P < Q and self.get_line_color(P, Q):
                    for S in 'ABCDEF':
                        if S > Q and self.get_line_color(P, Q) == self.get_line_color(Q, S) == self.get_line_color(P, S):
                            return [self.__make_edge(P, Q), self.__make_edge(Q, S), self.__make_edge(S, P)]
        return []
