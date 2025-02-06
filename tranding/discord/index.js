const { exec } = require('child_process');
const path = require('path');
const fs = require('fs');
const { promisify } = require('util');
const { Client, GatewayIntentBits, REST, Routes, SlashCommandBuilder, ButtonBuilder, ButtonStyle, ActionRowBuilder, Events } = require('discord.js');
const schedule = require('node-schedule');
const { channel } = require('diagnostics_channel');
require('dotenv').config({ path: './token and something.env' });

// 從環境變數中讀取值
const token = process.env.DISCORD_TOKEN;//token
const clientId = process.env.DISCORD_CLIENT_ID;// Application id
const guildId = process.env.DISCORD_GUILD_ID;//伺服器id
const channelId = process.env.DISCORD_CHANNEL_ID;//頻道id

const execPromise = promisify(exec);

// Create a new client instance
const client = new Client({ intents: [GatewayIntentBits.Guilds, GatewayIntentBits.GuildMessages, GatewayIntentBits.MessageContent] });

client.once(Events.ClientReady, async c => {
    console.log(`Ready! Logged in as ${c.user.tag}`);
    
    const channel = client.channels.cache.get(channelId); // 替換為你的頻道 ID
    if (channel) {
        // 發送開機完成消息
        await channel.send('老婆醬準備上班dayo！');

        // 立即執行一次功能
        await executeHourlyTask(true,null);

        //channel.send('等下 還有24H漲幅榜dayo');
        // await executeAndSendImage(channel)

        // 設置定時器每小時執行一次功能
        setInterval(async() => {
            await channel.send(' @Young,87878 馬的 1小時到了 該賺錢了 yoyo');
            await executeHourlyTask(channel);
        }, 3600000); // 每3600000毫秒（1小時）執行一次

        // 每天早上8點執行
        schedule.scheduleJob('0 8 * * *', async () => {
            await channel.send('@everyone 早安 該賺錢了 yoyo');
            await executeAndSendImage(channel);
        });
    }
});

// 監聽消息事件
client.on(Events.MessageCreate, message => {
    const channel = client.channels.cache.get(channelId); // 替換為你的頻道 ID
    // Ignore messages from the bot itself
    if (message.author.bot) return;

    // Respond to a specific command
    if (message.content === '!owo') {
        execute4HourlyTask(channel);
    }
});

// 定義斜杠命令
const commands = [
    new SlashCommandBuilder()
        .setName('搜尋')
        .setDescription('搜尋幣種')
        .addStringOption(option => 
            option.setName('coin')
                .setDescription('要搜尋的幣種')
                .setRequired(true)
                .setAutocomplete(true) // 啟用自動完成
        )
        .addStringOption(option => 
            option.setName('time')
                .setDescription('時間級別(沒選擇以5m圖呈上')
                .setRequired(false)
                .addChoices(
                    { name: '1m', value: '1m' },
                    { name: '5m', value: '5m' },
                    { name: '15m', value: '15m' },
                    { name: '1h', value: '1h' },
                    { name: '4h', value: '4h' },
                    { name: '1d', value: '1d' }
                )
        ),
    new SlashCommandBuilder().setName('owo').setDescription('查看大盤走勢(時區)'),
    new SlashCommandBuilder().setName('調教列表').setDescription('目前所有指令'),
    new SlashCommandBuilder().setName('ping').setDescription('Replies with Pong!'),
]
    .map(command => command.toJSON());

// 創建 REST 實例並設置 token
const rest = new REST({ version: '10' }).setToken(token);

// 註冊斜杠命令
(async () => {
    try {
        console.log('Started refreshing application (/) commands.');

        await rest.put(
            Routes.applicationGuildCommands(clientId, guildId),
            { body: commands },
        );

        console.log('Successfully reloaded application (/) commands.');
    } catch (error) {
        console.error(error);
    }
})();

client.once('ready', () => {
    console.log(`Ready! Logged in as ${client.user.tag}`);
});

// 監聽自動完成請求
client.on('interactionCreate', async interaction => {
    if (!interaction.isAutocomplete()) return;

    const focusedOption = interaction.options.getFocused(true);

    if (focusedOption.name === 'coin') {
        const alltradePath = 'C:\\Users\\Rushia is boingboing\\Downloads\\discord-Klinebot\\tranding\\github\\pybit-5.7.0\\examples\\alltrade.json';
        const alltrade = JSON.parse(fs.readFileSync(alltradePath, 'utf-8'));

        const choices = alltrade.map(trade => trade.Symbol);
        const filtered = choices.filter(choice => choice.toLowerCase().includes(focusedOption.value.toLowerCase()));

        await interaction.respond(
            filtered.slice(0, 25).map(choice => ({ name: choice, value: choice })),
        );
    } 
});

// 監聽斜杠命令
client.on('interactionCreate', async interaction => {
    const channel = client.channels.cache.get(channelId); // 替換為你的頻道 ID
    if (!interaction.isCommand()) return;

    const { commandName, options } = interaction;

    if (commandName === '搜尋') {
        const searchText = options.getString('coin');
        const timeRange = options.getString('time');
        // 讀取 alltrade.json 文件
        const alltradePath = 'C:\\Users\\Rushia is boingboing\\Downloads\\discord-Klinebot\\tranding\\github\\pybit-5.7.0\\examples\\alltrade.json';
        const alltrade = JSON.parse(fs.readFileSync(alltradePath, 'utf-8'));

        // 搜尋符合條件的 Symbol
        const results = alltrade.filter(trade => trade.Symbol.includes(searchText)).map(trade => trade.Symbol);

        // 保存用戶選擇到 userchose.txt
        const userChoice = `symbol=${searchText} \ntime=${timeRange || '未指定'}\n`;
        fs.writeFileSync('userchose.txt', userChoice);

        // 發送結果到 Discord 頻道
        await interaction.deferReply({ ephemeral: true }); // 延遲回應，以避免錯誤

        setTimeout(async () => {
            await interaction.followUp({ content: 'K線圖加載中dayo', ephemeral: true });
            await executechose(false, interaction); // 傳遞 interaction 參數
        }, 1000);
    } else if (commandName === '調教列表') {
        await interaction.reply({content:'目前有以下指令: \n/搜尋 可尋找需要幣種 \n/owo 呼叫按鈕區塊(看大盤走勢) \n/ping', ephemeral: true});   
    } else if (commandName === 'owo') {
        await executeButtonTask(false,interaction);
    } else if (commandName === 'ping') {
        await interaction.reply('Pong!');
    }
});

// 監聽按鈕互動事件
client.on('interactionCreate', async interaction => {
    const channel = client.channels.cache.get(channelId); // 替換為你的頻道 ID

    if (!interaction.isButton()) return;

    // 延遲回應，以避免錯誤
    await interaction.deferReply({ ephemeral: true });

    // 主按鈕區塊
    if (interaction.customId.startsWith('primary_')) {
        const timeRange = interaction.customId.split('_')[1];
            // 修改 userchose.txt 的 time 為用戶選擇的按鈕值
            const userChoicePath = 'userchose.txt';
            const userChoice = fs.readFileSync(userChoicePath, 'utf-8');
            const updatedUserChoice = userChoice.replace(/time=.*\n/, `time=${timeRange}\n`);
            fs.writeFileSync(userChoicePath, updatedUserChoice);
        setTimeout(async () => {
            await interaction.followUp({ content: `${timeRange} K線圖加載中dayo`, ephemeral: true });
            await executebigchose(interaction); // 傳遞 interaction 參數
        }, 1000);
    } else if (interaction.customId === 'primary_highline') {
        setTimeout(async () => {
            await interaction.editReply({ content: '漲幅榜加載中dayo', ephemeral: true });
            await executeAndSendImage(channel);
        }, 10000);
    } else if (interaction.customId === 'primary_nothing') {
        await interaction.editReply({ content: '什麼都不做dayo', ephemeral: true });

    } else if (interaction.customId.startsWith('chose_')) {
        const timeRange = interaction.customId.split('_')[1];
            // 修改 userchose.txt 的 time 為用戶選擇的按鈕值
            const userChoicePath = 'userchose.txt';
            const userChoice = fs.readFileSync(userChoicePath, 'utf-8');
            const updatedUserChoice = userChoice.replace(/time=.*\n/, `time=${timeRange}\n`);
            fs.writeFileSync(userChoicePath, updatedUserChoice);
        
        setTimeout(async () => {
            await interaction.editReply({ content: `${timeRange} K線圖加載中dayo`, ephemeral: true });
            await executechose(false, interaction); // 傳遞 interaction 參數
        }, 1000);
    }
});

// Log in to Discord with your client's token
client.login(token);

// 按鈕區塊
async function executeButtonTask(isSystemCall, interaction) {
    try {
        const messageContent = '呼叫的按鈕區塊呈上:dayo';
        const followUpMessage = '需要什麼再按一下或/調教列表dayo';
        // 1m
        const oneminute = new ButtonBuilder()
            .setCustomId('primary_1m')
            .setLabel('1m')
            .setStyle(ButtonStyle.Primary);
        // 5m
        const fiveminute = new ButtonBuilder()
            .setCustomId('primary_5m')
            .setLabel('5m')
            .setStyle(ButtonStyle.Primary);
        // 15m
        const fifteenminute = new ButtonBuilder()
            .setCustomId('primary_15m')
            .setLabel('15m')
            .setStyle(ButtonStyle.Primary);
        // 30m
        const thirtyminute = new ButtonBuilder()
            .setCustomId('primary_30m')
            .setLabel('30m')
            .setStyle(ButtonStyle.Primary);
        // 1h
        const onehour = new ButtonBuilder()
            .setCustomId('primary_1h')
            .setLabel('1h')
            .setStyle(ButtonStyle.Primary);
        // 4h
        const fourhour = new ButtonBuilder()
            .setCustomId('primary_4h')
            .setLabel('4h')
            .setStyle(ButtonStyle.Primary);
        // nothing
        const nothing = new ButtonBuilder()
            .setCustomId('chose_nothing')
            .setLabel('什麼都不做 重新把/owo')
            .setStyle(ButtonStyle.Secondary);

        const row1 = new ActionRowBuilder().addComponents(oneminute, fiveminute, fifteenminute);
        const row2 = new ActionRowBuilder().addComponents(thirtyminute, onehour, fourhour);
        const row3 = new ActionRowBuilder().addComponents(nothing);
        if (isSystemCall) {
            // 系統呼叫，輸出到伺服器
            const channel = client.channels.cache.get(channelId); // 替換為你的頻道 ID
            if (channel) {
                await channel.send({
                    content: `${followUpMessage} (以下為主流盤時區)`,
                    components: [row1, row2]
                });
            } else {
                console.error('Channel not found');
            }
        } else if (interaction) {
            // 用戶按鈕呼叫，回應用戶
            await interaction.reply({
                content: `${messageContent}\n${followUpMessage}`,'有5秒cd': true,
                ephemeral: true,
                components: [row1, row2]
            });
            setTimeout(async () => {
                await interaction.editReply({
                    content: `${messageContent}\n${followUpMessage}`,'什麼都不做 重新把/owo': true,
                    ephemeral: true,
                    components: [row3]
                });
            }, 5000); // 5秒後啟用按鈕
        }
    
    } catch (error) {
        console.error(`exec error: ${error}`);
    }
}


// 漲幅榜
async function executeAndSendImage(channel) {
    try {
        channel.send('送上24H漲幅榜dayo');
        await execPromise('python "C:\\Users\\Rushia is boingboing\\Downloads\\discord-Klinebot\\tranding\\github\\pybit-5.7.0\\examples\\allhightrade.py"');

        // 讀取輸出結果文件
        const outputFilePath = 'C:\\Users\\Rushia is boingboing\\Downloads\\discord-Klinebot\\tranding\\github\\pybit-5.7.0\\examples\\output.txt';
        const data = await fs.promises.readFile(outputFilePath, 'utf-8');

        // 發送輸出結果到 Discord 頻道
        const messages = data.split('\n').filter(Boolean);
        for (const message of messages) {
            await channel.send(message);
            // 發送對應的 K 線圖
            const symbol = message.split(' ')[1].replace(':', '');
            const imagePath = path.join('C:\\Users\\Rushia is boingboing\\Downloads\\discord-Klinebot\\tranding\\discord\\K highline', `${symbol}_Kline.png`);
            try {
                await fs.promises.access(imagePath, fs.constants.F_OK);
                await channel.send({ files: [imagePath] });
                console.log(`圖片已發送: ${imagePath}`);
            } catch (err) {
                console.error(`圖片不存在: ${imagePath}`);
            }
        }
        await channel.send('需要什麼再按一下或/調教列表dayo');
    } catch (error) {
        console.error(`exec error: ${error}`);
    }
}

// 每小時K線圖
async function executeHourlyTask(isSystemCall, interaction) {
    try {
        const { stdout } = await execPromise('python "C:\\Users\\Rushia is boingboing\\Downloads\\discord-Klinebot\\tranding\\github\\pybit-5.7.0\\examples\\K linetest.py"');
        const { Ethstdout } = await execPromise('python "C:\\Users\\Rushia is boingboing\\Downloads\\discord-Klinebot\\tranding\\github\\pybit-5.7.0\\examples\\EthKline.py"');
        
        const messages = {
            hourlyTask: '每小時任務輸出結果:',
            btcMessage: 'BTC1小時K線圖',
            ethMessage: 'ETH1小時K線圖',
            followUpMessage: '需要什麼再按一下或/調教列表dayo'
        };
        const imagePath = path.join('C:\\Users\\Rushia is boingboing\\Downloads\\discord-Klinebot\\tranding\\discord\\K line', `Klinetest.png`);
        const EthimagePath = path.join('C:\\Users\\Rushia is boingboing\\Downloads\\discord-Klinebot\\tranding\\discord\\K line', `EthKlinetest.png`);

        if (isSystemCall) {
            // 系統呼叫，輸出到伺服器
            const channel = client.channels.cache.get(channelId); // 替換為你的頻道 ID
            if (channel) {
                await channel.send(messages.hourlyTask);
                await channel.send(messages.btcMessage);
                try {
                    await fs.promises.access(imagePath, fs.constants.F_OK);
                    await channel.send({ files: [imagePath] });
                    console.log(`圖片已發送: ${imagePath}`);
                } catch (err) {
                    console.error(`圖片不存在: ${imagePath}`);
                }
                await channel.send(messages.ethMessage);
                try {
                    await fs.promises.access(EthimagePath, fs.constants.F_OK);
                    await channel.send({ files: [EthimagePath] });
                    console.log(`圖片已發送: ${EthimagePath}`);
                } catch (err) {
                    console.error(`圖片不存在: ${EthimagePath}`);
                }
            } else {
                console.error('Channel not found');
            }
        } else if (interaction) {
            // 用戶按鈕呼叫，回應用戶
            const replyMessages = [
                { content: messages.hourlyTask, ephemeral: true },
                { content: messages.btcMessage, ephemeral: true },
                { files: [imagePath], ephemeral: true },
                { content: messages.ethMessage, ephemeral: true },
                { files: [EthimagePath], ephemeral: true },
                { content: messages.followUpMessage, ephemeral: true }
            ];

            const files = [];
            try {
                await fs.promises.access(imagePath, fs.constants.F_OK);
                files.push(imagePath);
                console.log(`圖片已發送: ${imagePath}`);
            } catch (err) {
                console.error(`圖片不存在: ${imagePath}`);
            }
            try {
                await fs.promises.access(EthimagePath, fs.constants.F_OK);
                files.push(EthimagePath);
                console.log(`圖片已發送: ${EthimagePath}`);
            } catch (err) {
                console.error(`圖片不存在: ${EthimagePath}`);
            }

            await interaction.editReply({
                content: `${messages.hourlyTask}\n${messages.btcMessage}\n${messages.ethMessage}\n`,
                files: files,
                ephemeral: true
            });
        }
        await executeButtonTask(true, null);
    } catch (error) {
        console.error(`exec error: ${error}`);
    }
}

// 每大盤區間K線圖
async function executebigchose(interaction) {
    try {
        const { stdout } = await execPromise('python "C:\\Users\\Rushia is boingboing\\Downloads\\discord-Klinebot\\tranding\\github\\pybit-5.7.0\\examples\\mainchose.py"');
        const messages = {
            hourlyTask: '呼叫的主流盤結果:dayo',
            followUpMessage: '需要什麼再按一下或/調教列表dayo'
        };
        const imagePath1 = path.join('C:\\Users\\Rushia is boingboing\\Downloads\\discord-Klinebot\\tranding\\discord\\K line', `BTCUSDT.png`);
        const imagePath2 = path.join('C:\\Users\\Rushia is boingboing\\Downloads\\discord-Klinebot\\tranding\\discord\\K line', `ETHUSDT.png`);
        // 用戶按鈕呼叫，回應用戶
        const replyMessages = [
            { content: messages.hourlyTask, ephemeral: true },
            { content: messages.btcMessage, ephemeral: true },
            { files: [imagePath1,imagePath2], ephemeral: true },
            { content: messages.followUpMessage, ephemeral: true }
        ];

        const files = [];
        try {
            await fs.promises.access(imagePath1, fs.constants.F_OK);
            files.push(imagePath1);
            files.push(imagePath2);
            console.log(`圖片已發送: ${imagePath1}${imagePath2}`);
        } catch (err) {
            console.error(`圖片不存在: ${imagePath1}`);
        }

        await interaction.editReply({
            content: `${messages.hourlyTask}\n${messages.followUpMessage}\n`,
            files: files,
            ephemeral: true
        });
    } catch (error) {
        console.error(`exec error: ${error}`);
        }
}

// 選擇K線圖
async function executechose(isSystemCall, interaction) {
    try {
        await execPromise('python "C:\\Users\\Rushia is boingboing\\Downloads\\discord-Klinebot\\tranding\\github\\pybit-5.7.0\\examples\\choseKline.py"');
        
        const messageContent = '呼叫的指定圖呈上:dayo';
        const imagePath = path.join('C:\\Users\\Rushia is boingboing\\Downloads\\discord-Klinebot\\tranding\\discord\\user', `chose.png`);
        const files = [];

        try {
            await fs.promises.access(imagePath, fs.constants.F_OK);
            files.push(imagePath);
            console.log(`圖片已發送: ${imagePath}`);
        } catch (err) {
            console.error(`圖片不存在: ${imagePath}`);
        }

        const followUpMessage = '需要什麼再按一下或/調教列表dayo';

        // 1m
        const oneminute = new ButtonBuilder()
            .setCustomId('chose_1m')
            .setLabel('1m')
            .setStyle(ButtonStyle.Primary);
        // 5m
        const fiveminute = new ButtonBuilder()
            .setCustomId('chose_5m')
            .setLabel('5m')
            .setStyle(ButtonStyle.Primary);
        // 15m
        const fifteenminute = new ButtonBuilder()
            .setCustomId('chose_15m')
            .setLabel('15m')
            .setStyle(ButtonStyle.Primary);
        // 30m
        const thirtyminute = new ButtonBuilder()
            .setCustomId('chose_30m')
            .setLabel('30m')
            .setStyle(ButtonStyle.Primary);
        // 1h
        const onehour = new ButtonBuilder()
            .setCustomId('chose_1h')
            .setLabel('1h')
            .setStyle(ButtonStyle.Primary);
        // 4h
        const fourhour = new ButtonBuilder()
            .setCustomId('chose_4h')
            .setLabel('4h')
            .setStyle(ButtonStyle.Primary);
        // nothing
        const nothing = new ButtonBuilder()
            .setCustomId('chose_nothing')
            .setLabel('什麼都不做 重新把/owo')
            .setStyle(ButtonStyle.Secondary);

        const row1 = new ActionRowBuilder().addComponents(oneminute, fiveminute, fifteenminute);
        const row2 = new ActionRowBuilder().addComponents(thirtyminute, onehour, fourhour);
        const row3 = new ActionRowBuilder().addComponents(nothing);
        if (isSystemCall) {
            // 系統呼叫，輸出到伺服器
            const channel = client.channels.cache.get(channelId); // 替換為你的頻道 ID
            if (channel) {
                await channel.send({
                    content: `${messageContent}\n${followUpMessage}`,
                    files: files,
                    components: [row1, row2]
                });
            } else {
                console.error('Channel not found');
            }
        } else if (interaction) {
            // 用戶按鈕呼叫，回應用戶
            await interaction.editReply({
                content: `${messageContent}\n${followUpMessage}`,'有5秒cd': true,
                files: files,
                ephemeral: true,
                components: [row1, row2]
            });
            
        }
        setTimeout(async () => {
            await interaction.editReply({
                content: `${messageContent}\n${followUpMessage}`,'什麼都不做 重新把/owo': true,
                files: files,
                ephemeral: true,
                components: [row3]
            });
        }, 5000); // 5秒後啟用按鈕
    
    } catch (error) {
        console.error(`exec error: ${error}`);
    }
}
