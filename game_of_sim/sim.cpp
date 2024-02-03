#include <bits/stdc++.h>

using namespace std;

class Sim {
private:
    int onMove = 1;
    bool finished = false;
    vector<string> edge_labels;
    vector<string> R, RvB, B, moves;
    map<string, int> edge_colors; // 0 not colored yet, 1 red, 2 blue
    string move10 = "", move12 = "";
    void normalizeEdge(string &edge) {
        if (edge.length() != 2 || edge[0]==edge[1]
            || edge[0]<'A' || edge[0]>'F'
            || edge[1]<'A' || edge[1]>'F')
            throw invalid_argument("Invalid edge label");
        if (edge[0] > edge[1]) swap(edge[0], edge[1]);
    }
    string makeEdge(char P, char Q) {
        auto ans = string(1, P) + Q;
        normalizeEdge(ans);
        return ans;
    }
    bool edgeFromVertex(string PQ, char P) {
        return PQ[0] == P || PQ[1] == P;
    }
    char commonVertex(string PQ, string PR) {
        if (PQ[0] == PR[0]) return PQ[0];
        if (PQ[0] == PR[1]) return PQ[0];
        if (PQ[1] == PR[0]) return PQ[1];
        if (PQ[1] == PR[1]) return PQ[1];
        throw invalid_argument("Invalid labels");
    }
    bool checkGameFinished() {
        for(auto &PQ: edge_labels) {
            if (edge_colors[PQ] == 0) continue;
            int colorPQ = getEdgeColor(PQ);
            for(char R = 'A'; R<='F'; R++) {
                if (R==PQ[0] || R==PQ[1]) continue;
                string PR = makeEdge(PQ[0], R);
                string QR = makeEdge(PQ[1], R);
                if (getEdgeColor(PR)==colorPQ && getEdgeColor(QR)==colorPQ) {
                    finished = true;
                    return finished;
                }
            }
        }
        return finished;
    }

    bool isPlayable(string PQ, int color) {
        if (edge_colors[PQ]) return false;
        for(char R = 'A'; R<='F'; R++) {
            if (R==PQ[0] || R==PQ[1]) continue;
            string PR = makeEdge(PQ[0], R);
            string QR = makeEdge(PQ[1], R);
            if (getEdgeColor(PR)==color && getEdgeColor(QR)==color) return false;
        }
        return true;
    }

    void computePlayableEdges() {
        R.clear(); B.clear(); RvB.clear();
        for(auto &PQ: edge_labels) {
            if (edge_colors[PQ] > 0) continue;
            bool redPlayable = isPlayable(PQ, 1);
            bool bluePlayable = isPlayable(PQ, 2);
            if (redPlayable) {
                if (bluePlayable) RvB.push_back(PQ);
                else R.push_back(PQ);
            } else if (bluePlayable) B.push_back(PQ);
        }
    }

    vector<string> computeMinX() {
        map<string, int> Xs;
        for(auto QS: RvB) {
            edge_colors[QS] = 2;
            Xs[QS] = 0;
            for(auto PQ: RvB) {
                if (PQ != QS && !isPlayable(PQ, 2)) Xs[QS]++;//PQ is lost up on playing on QS
            }
            for(auto PQ: B) {
                if (PQ != QS && !isPlayable(PQ, 2)) Xs[QS]++;//PQ is lost up on playing on QS
            }
            edge_colors[QS] = 0;
        }
        vector<pair<int, string>> X;
        for(auto [edge, val]: Xs) X.emplace_back(val, edge);
        sort(X.begin(), X.end());
        // debug(X);
        vector<string> ans; ans.push_back(X[0].second);
        for(int i=1; i<X.size(); i++) {
            if (X[i].first == X[0].first) ans.push_back(X[i].second);
        }
        return ans;
    }

    int computeZ(string ij) {
        int ans = 0;
        for(char k='A'; k<='F'; k++) {
            if (k==ij[0] || k==ij[1]) continue;
            string ik = makeEdge(ij[0], k);
            string jk = makeEdge(ij[1], k);
            if (isPlayable(ik, 2) && isPlayable(jk, 2)) ans+=2;
            else if (edge_colors[ik] == 1 && isPlayable(jk, 1)) ans++;
            else if (edge_colors[jk] == 1 && isPlayable(ik, 1)) ans++;
        }
        return ans;
    }

    string getBestMove() {
        computePlayableEdges();
        vector<string> Xs = computeMinX();
        if (Xs.size() == 1) return Xs[0];
        vector<pair<int, string>> Zs;
        for(string ij: Xs) {
            int z=computeZ(ij);
            Zs.emplace_back(z, ij);
        }
        sort(Zs.begin(), Zs.end());
        // debug(Zs);
        return Zs[0].second;
    }

public:
    Sim() {
        reset();
    }

    void reset() {
        onMove = 1;
        moves.clear();
        finished = false;
        if (edge_labels.empty()) {
            for(char P='A'; P<'F'; P++) {
                for(char Q=P+1; Q<='F'; Q++) {
                    edge_labels.push_back(makeEdge(P, Q));
                }
            }
        }
        edge_colors.clear();
        for(auto &label: edge_labels) edge_colors[label] = 0;
    }

    void play(string PQ) {
        normalizeEdge(PQ);
        if (finished) throw logic_error("The game has been finished");
        if (getEdgeColor(PQ) > 0) throw logic_error("This move is already played");
        moves.push_back(PQ);
        edge_colors[PQ] = 2 - (onMove%2);
        onMove++;
        checkGameFinished();
        if (useEngine && !finished && isBlueTurn()) {//machine to play
            if (onMove == 2) { // Rule 1
                for(char R='A'; R<'F'; R++) {
                    if (R != PQ[0] && R != PQ[1]) {
                        play(makeEdge(PQ[0], R));
                        return;
                    }
                }
            } else if (onMove == 4) { // Rule 2
                set<char> st;
                for(auto &edge: moves) {
                    st.insert(edge[0]); st.insert(edge[1]);
                }
                if (st.size() == 3) { //3 first moves make a triangle
                    string PR = moves[0];
                    char P = commonVertex(PR, PQ);
                    for(int i=edge_labels.size()-1; i>=0; i--) {
                        if (!edge_colors[edge_labels[i]] && edgeFromVertex(edge_labels[i], P)) {
                            play(edge_labels[i]);
                            return;
                        }
                    }
                } else {
                    char V = commonVertex(moves[0], moves[1]);
                    char R = moves[0][0] == V ? moves[0][1] : moves[0][0];
                    char S = moves[1][0] == V ? moves[1][1] : moves[1][0];
                    play(makeEdge(R, S));
                    return;
                }
            } else if (onMove == 6 || onMove == 8) {
                string bestMove = getBestMove(); // Rule 3
                play(bestMove);
                return;
            } else if (onMove == 10) {
                move10 = move12 = "";
                computePlayableEdges();
                if (R.size() == 1 && RvB.size() == 2 && B.size() == 3) { //Rule 4
                    for(auto side1: RvB) {
                        edge_colors[side1] = 2;
                        for(auto side2: B) {
                            if (isPlayable(side2, 2)) {
                                edge_colors[side2] = 2;
                                for(auto side3: B) {
                                    if (side3 != side2 && isPlayable(side3, 2)) {
                                        move10 = side1; move12 = side2;
                                        break;
                                    }
                                }
                                edge_colors[side2] = 0;
                            }
                        }
                        edge_colors[side1] = 0;
                    }
                    play(move10);
                    return;
                } else if (R.size() == 1 && RvB.size() == 3 && B.size() == 2) { //Rule 5: "AF", "AB", "BF", "EF", "CD", "CF", "BE", "AE", "DF"
                    for(auto side1: RvB) {
                        edge_colors[side1] = 2;
                        bool rule5_best_move = true;
                        for(auto side2: RvB) {
                            if (side2 == side1) continue;
                            if (!isPlayable(side2, 2)) {
                                rule5_best_move = false;
                                break;
                            }
                        }
                        edge_colors[side1] = 0;
                        if (rule5_best_move) {
                            play(side1);
                            return;
                        }
                    }
                    throw logic_error("Strategy not found on move " + to_string(onMove));
                } else {
                    // PrintAnalysis();
                    string bestMove = getBestMove(); // Rule 3
                    play(bestMove);
                    return;
                }
            } else if (onMove == 12) {
                if (move12 != "") { // Rule 4
                    play(move12);
                } else {
                    computePlayableEdges();
                    // PrintAnalysis();
                    if (!RvB.empty()) {
                        play(RvB[0]);
                    } else if (!B.empty()) {
                        play(B[0]);
                    } else {
                        // PrintAnalysis();
                        throw logic_error("Strategy not found on move " + to_string(onMove));
                    }
                }
                return;
            } else if (onMove == 14) {
                computePlayableEdges();
                if (!RvB.empty()) {
                    play(RvB[0]);
                } else if (!B.empty()) {
                    play(B[0]);
                } else {
                    // PrintAnalysis();
                    throw logic_error("Strategy not found on move " + to_string(onMove));
                }
            }
        }
    }

    bool useEngine = true;
    vector<string> getMoves() {return moves;}
    bool isRedTurn() { return onMove % 2 == 1; }
    bool isBlueTurn() { return onMove % 2 == 0; }
    bool isFinished() { return finished; }
    int getEdgeColor(string edge) {
        normalizeEdge(edge);
        return edge_colors[edge];
    }
    int getEdgeColor(char P, char Q) {
        string edge = makeEdge(P, Q);
        return getEdgeColor(edge);
    }
    vector<string> getTriangleEdges() {
        if (!finished) return {};
        for(char P='A'; P<='F'; P++) {
            for(char Q=P+1; Q<='F'; Q++) {
                if (!getEdgeColor(P, Q)) continue;
                for(char S=Q+1; S<='F'; S++) {
                    if (getEdgeColor(P, Q) == getEdgeColor(Q, S) && getEdgeColor(P, Q) == getEdgeColor(P, S)) {
                        return {makeEdge(P, Q), makeEdge(Q, S), makeEdge(S, P)};
                    }
                }
            }
        }
        return {};
    }

    // void PrintAnalysis() {
    //     debug(getMoves());
    //     computePlayableEdges();
    //     debug(R);
    //     debug(RvB);
    //     debug(B);
    // }
};

signed main() {
    Sim sim;
    try {
        sim.play("AF");
        sim.play("FB");
        sim.play("CD");
        sim.play("EB");
        sim.play("DF");
        sim.play("AC");
        sim.play("CE");
        // sim.PrintAnalysis();
        // if (sim.isFinished()) {
        //     debug(sim.getTriangleEdges());
        // }
    }
    catch(const invalid_argument &e) {
        cerr << "Error: " << e.what() << "\n";
    }
    catch(const logic_error &e) {
        cerr << "Error: " << e.what() << "\n";
    }
    return 0;
}