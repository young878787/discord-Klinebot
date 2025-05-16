import matplotlib.pyplot as plt
import numpy as np
import os

# 確保 K line 資料夾存在
if not os.path.exists('Kline'):
    os.makedirs('Kline')

# 簡單的數據
x = np.linspace(0, 10, 100)
y = np.sin(x)

plt.plot(x, y)
plt.title('Test Plot')
plt.xlabel('X-axis')
plt.ylabel('Y-axis')

# 儲存圖片
plt.savefig('Kline/test_plot.png')
plt.show()