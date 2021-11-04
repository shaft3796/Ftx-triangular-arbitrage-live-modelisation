from matplotlib import pyplot as plt, animation
from private.ObtFtxLive import FtxLiveClient

client = FtxLiveClient('api_key', 'api_secret')

pair1 = "SXP/USD"
pair2 = "BTC/USD"
mid_pair = "SXP/BTC"
amount = 25

xar = []
yar = []
yar2 = []
fig = plt.figure()
ax1 = fig.add_subplot(1, 1, 1)
ax1.set_xlabel("Profit")
ax1.set_title("USD SCP BTC - Triangular arbitrage")


def animate(i):
    pair1_price_classic = client.get_buy_price(pair1)
    pair2_price_classic = client.get_sell_price(pair2)
    mid_pair_price_classic = client.get_sell_price(mid_pair)
    pair1_price_reverse = client.get_buy_price(pair1)
    pair2_price_reverse = client.get_buy_price(pair2)
    mid_pair_price_reverse = client.get_sell_price(mid_pair)

    token_1 = (amount / pair1_price_classic) * (1 - 0.00065)
    token_2 = (token_1 * mid_pair_price_classic) * (1 - 0.00065)
    coin_time1 = (token_2 * pair2_price_classic) * (1 - 0.00065)
    token_2 = (amount / pair2_price_reverse) * (1 - 0.00065)
    token_1 = (token_2 / mid_pair_price_reverse) * (1 - 0.00065)
    coin_time2 = (token_1 * pair1_price_reverse) * (1 - 0.00065)
    print("----------------------------")
    print(coin_time1 - amount, "By coin 1")
    print(coin_time2 - amount, "By coin 2")

    global xar
    global ax1
    global yar
    global yar2
    xar.append(i)
    yar.append(coin_time1 - amount)
    yar2.append(coin_time2 - amount)
    ax1.clear()
    ax1.set_ylabel("Profit")
    ax1.set_title("USD SXP BTC - Triangular arbitrage")
    ax1.plot(xar, yar, color="green", linewidth="2")
    ax1.plot(xar, yar2, color="red", linewidth="2")
    ax1.plot([0, i], [0, 0], color="purple", linewidth="1", linestyle='dashed')


ani = animation.FuncAnimation(fig, animate, interval=1)
plt.show()
