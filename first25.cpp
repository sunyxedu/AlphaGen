#include <bits/stdc++.h>
using namespace std;
namespace First25 {
	const int N = 55;
	const int limit = 100;
	const double eps = 1e-9;
	const vector<pair<int, int>> dir = {{1, 0}, {-1, 0}, {0, 1}, {0, -1}};
	vector<vector<int>> dis;
	vector<vector<double>> weight;
	queue<pair<int, int>> q;
	struct Move {
		int step, x, y, x1, y1;
	};
	struct State {
		int x, y;
		double weight;
		vector<vector<int>> army;
		vector<Move> moves;
	};
	vector<State> states[N][N];

	bool operator < (State state, State state1) {
		if(abs(state.weight - state1.weight) > eps)
			return state.weight > state1.weight;
		return state.army < state1.army;
	}
	bool operator == (State state, State state1) {
		return state.army == state1.army;
	}
	void sort_states(vector<State> &states) {
		sort(states.begin(), states.end());
		states.resize(min<int>(unique(states.begin(), states.end()) - states.begin(), limit));
	}
	void solve(int height, int width, int sx, int sy, vector<vector<int>> obs) {
		dis.resize(height);
		for(auto &a : dis) {
			a.resize(width);
			fill(a.begin(), a.end(), -1);
		}
		weight.resize(height);
		for(auto &a : weight) a.resize(width);
		dis[sx][sy] = 0;
		q.push({sx, sy});
		while(!q.empty()) {
			auto [x, y] = q.front();
			q.pop();
			for(auto [dx, dy] : dir) {
				int x1 = x + dx, y1 = y + dy;
				if(x1 >= 0 && x1 < height && y1 >= 0 && y1 < width && obs[x1][y1] == 0 && dis[x1][y1] == -1) {
					dis[x1][y1] = dis[x][y] + 1;
					q.push({x1, y1});
				}
			}
		}
		for(int i = 0; i < height; ++i)
			for(int j = 0; j < width; ++j)
				weight[i][j] = dis[i][j];
		State initial_state;
		initial_state.army.resize(height);
		for(auto &a : initial_state.army) a.resize(width);
		initial_state.x = sx;
		initial_state.y = sy;
		initial_state.weight = 0;
		initial_state.moves = {};
		states[0][1].push_back(initial_state);
		for(int step = 0; step < 50; ++step)
			for(int land = 1; land <= step / 2 + 1; ++land) {
				if(step % 2 == 0)
					for(auto &state : states[step][land]) {
						++state.army[sx][sy];
						state.weight += weight[sx][sy];
					}
				sort_states(states[step][land]);
				// printf("step = %d land = %d size = %d\n", step, land, states[step][land].size());
				for(auto state : states[step][land]) {
					int x = state.x, y = state.y;
					int t = state.army[x][y] - 1;
					if(t == 0) {
						x = sx;
						y = sy;
						t = state.army[x][y] - 1;
					}
					if(x == sx && y == sy)
						states[step + 1][land].push_back(state);
					if(t == 0) continue;
					for(auto [dx, dy] : dir) {
						int x1 = x + dx, y1 = y + dy;
						if(x1 >= 0 && x1 < height && y1 >= 0 && y1 < width && obs[x1][y1] == 0) {
							State state1 = state;
							state1.x = x1;
							state1.y = y1;
							state1.weight += (weight[x1][y1] - weight[x][y]) * t;
							state1.army[x][y] -= t;
							state1.army[x1][y1] += t;
							state1.moves.push_back((Move) {step, x, y, x1, y1});
							states[step + 1][land + (state.army[x1][y1] == 0)].push_back(state1);
						}
					}
				}
			}
		for(int land = 50; land >= 1; --land)
			if(!states[50][land].empty()) {
				State state = states[50][land][0];
				printf("land = %d\n", land);
				for(auto [step, x, y, x1, y1] : state.moves)
					printf("step = %d (%d %d) -> (%d %d)\n", step, x, y, x1, y1);
				break;
			}
	}
}
int main() {
	int height, width, sx, sy;
	vector<vector<int>> obs;
	scanf("%d %d %d %d", &height, &width, &sx, &sy);
	obs.resize(height);
	for(auto &a : obs) {
		a.resize(width);
		for(auto &x : a) scanf("%d", &x);
	}
	First25::solve(height, width, sx, sy, obs);
}

/*
4 11 0 0
0 0 0 0 0 0 0 0 0 0 0
0 0 0 0 0 0 0 0 0 1 1
0 0 0 0 0 1 1 1 1 1 1
1 0 1 1 1 1 1 1 1 1 1

4 11 0 0
0 0 0 0 0 0 0 0 0 0 0
0 0 0 0 0 0 0 0 0 0 0
0 0 0 0 0 0 0 0 0 0 0
0 0 0 0 0 0 0 0 0 0 0

5 5 0 0
0 1 0 0 0
0 0 0 0 0
0 0 0 0 0
0 0 0 0 0
0 0 0 0 0

6 11 2 1
1 1 0 0 1 1 0 0 0 1 0
1 0 1 0 0 0 0 1 0 1 0
0 0 1 0 1 1 1 0 0 1 0
0 0 0 1 0 0 0 0 0 0 0
0 0 0 0 0 0 0 0 0 1 0
1 0 0 0 0 1 0 1 0 0 1

10 10 5 0
1 0 0 0 0 0 0 0 0 0
0 0 0 0 0 0 0 0 0 0
0 0 0 0 1 0 1 0 0 0
0 1 1 0 1 0 0 0 1 0
0 0 0 1 0 0 0 1 1 0
0 0 0 0 0 0 0 0 0 0
0 1 1 0 0 0 0 1 0 0
1 0 0 0 0 0 1 1 0 0
0 0 0 0 1 0 0 0 0 0
0 0 0 0 0 1 0 0 0 0
*/