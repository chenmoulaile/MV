// 题目：P17831 [CSP-S 2026] 能量水晶 / crystal（民间数据）
// 来源：https://www.luogu.com.cn/problem/P17831
// 时间限制：1000 ms
// 空间限制：1024 MB
#include <bits/stdc++.h>
// (^. .^)ʃ
typedef long long ll;

int main() {
	// freopen("crystal.in", "r", stdin);
	// freopen("crystal.out", "w", stdout);

	int n;
	ll m;
	scanf("%d%lld", &n, &m);

	std::vector<ll> a(n + 1);
	for (int i = 1; i <= n; i++)
		scanf("%lld", &a[i]);

	std::sort(a.begin() + 1, a.end());

	std::vector<ll> s(n + 1);
	for (int i = 1; i <= n; i++)
		s[i] = s[i - 1] + a[i];

	int ans = 0;
	for (int i = 1; i <= n; i++) {
		int L = 0, R = i + 1;
		while (L + 1 < R) {
			int M = (L + R) / 2;
			ll sum = s[i] - s[M - 1];
			ll tot = a[i] * ll(i - M + 1);
			if (tot - sum <= m) R = M;
			else L = M;
		}
		ans = std::max(ans, i - L);
	}

	printf("%d\n", ans);

	return 0;
}
