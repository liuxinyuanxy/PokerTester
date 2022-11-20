This is a tester based on [ACPCServer](https://github.com/liuxinyuanxy/ACPCServer)
Please pack your agent into a executable file  and put it in the same directory with this tester.
The tester will use below command to run your agent:
```shell
./your_agent_name config_file localhost port
# for example
# ./example_player config.game localhost 10000
```

The server will send the following information to your agent:
```shell
2:999:ccc/r8309cc/cr10409r17788c:||Qd3c/4d6d2d/5d
# Chinese version:
# 你的座位号：轮数：操作（用/隔开每一round）：零号位手牌|一号位手牌|二号位手牌/第一round出现的桌面牌（3张）/第二round出现的桌面牌（1张）/第三round出现的桌面牌（1张）
```