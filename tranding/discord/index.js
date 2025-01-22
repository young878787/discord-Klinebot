
const { exec } = require('child_process');
const path = require('path');
const fs = require('fs');
const { promisify } = require('util');
const { Client, GatewayIntentBits, REST, Routes, SlashCommandBuilder, ButtonBuilder, ButtonStyle, ActionRowBuilder,Events } = require('discord.js');
//const { token, clientId, guildId } = require('./config.json'); // 確保你有一個 config.json 文件，其中包含你的 Discord 機器人 token, clientId 和 guildId
require('dotenv').config({ path: './token and something.env' });

// 從環境變數中讀取值
const token = process.env.DISCORD_TOKEN;
const clientId = process.env.DISCORD_CLIENT_ID;
const guildId = process.env.DISCORD_GUILD_ID;
const channelId = process.env.DISCORD_CHANNEL_ID;

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
        await executeHourlyTask(channel);
        channel.send('等下 還有24H漲幅榜dayo');

        executeAndSendImage(channel);

        // 設置定時器每小時執行一次功能
        setInterval(async() => {
            await channel.send('@everyone 馬的 1小時到了 該賺錢了 yoyo');
            await executeHourlyTask(channel);
        }, 3600000); // 每3600000毫秒（1小時）執行一次

        setInterval(async() => {
            await channel.send('@everyone 早安 該賺錢了 yoyo');
            await executeAndSendImage(channel);
        }, 86400000); // 每3600000毫秒（1小時）執行一次
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
//指令區

// 定義斜杠命令
const commands = [
    //new SlashCommandBuilder().setName('button').setDescription('Replies with a button!'),
    new SlashCommandBuilder().setName('owo').setDescription('按鈕列表'),
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

// 監聽斜杠命令
client.on('interactionCreate', async interaction => {
    const channel = client.channels.cache.get(channelId); // 替換為你的頻道 ID
    if (!interaction.isCommand()) return;

    const { commandName } = interaction;

    if (commandName === 'owo') {
        //1h
        const onehour = new ButtonBuilder()
            .setCustomId('primary_1hour')
            .setLabel('1H')
            .setStyle(ButtonStyle.Primary);
        //4h
        const fourhour = new ButtonBuilder()
            .setCustomId('primary_4hour')
            .setLabel('4H')
            .setStyle(ButtonStyle.Primary);
        //漲符榜
        const highline = new ButtonBuilder()
            .setCustomId('primary_highline')
            .setLabel('漲幅榜')
            .setStyle(ButtonStyle.Primary);


        const row = new ActionRowBuilder().addComponents(onehour, fourhour, highline);

        
        await interaction.reply({
            content: '提供所有的時區',
            ephemeral: true,
            components: [row],
        });
    } else if (commandName === 'ping') {
        await interaction.reply('Pong!');
    }
});

// 監聽按鈕互動事件
client.on('interactionCreate', async interaction => {
    if (!interaction.isButton()) return;

    await interaction.deferReply({ ephemeral: true }); // 延遲回應，以避免錯誤

    if (interaction.customId === 'primary_1hour') {
        setTimeout(async () => {
            await interaction.followUp({ content: '1小時K線圖加載dayo', ephemeral: true });
            await executeHourlyTask(channelId);
        }, 10000);
    } else if (interaction.customId === 'primary_4hour') {
        setTimeout(async () => {
            await interaction.followUp({ content: '4小時K線圖加載dayo', ephemeral: true });
            await executeHourlyTask(channelId);
        }, 10000);
    } else if (interaction.customId === 'primary_highline') {
        setTimeout(async () => {
            await interaction.followUp({ content: '漲幅榜加載dayo', ephemeral: true });
            await executeAndSendImage(channelId);
        }, 10000);
    }
});
// Log in to Discord with your client's token
client.login(token);
//膜塊區
    //漲幅榜
async function executeAndSendImage(channel) {
    try {
        channel.send('送上24H漲幅榜dayo');
        await execPromise('python "C:\\Users\\Rushia is boingboing\\Desktop\\tranding\\github\\pybit-5.7.0\\examples\\allhightrade.py"');

        // 讀取輸出結果文件
        const outputFilePath = 'C:\\Users\\Rushia is boingboing\\Desktop\\tranding\\github\\pybit-5.7.0\\examples\\output.txt';
        const data = await fs.promises.readFile(outputFilePath, 'utf-8');

        // 發送輸出結果到 Discord 頻道
        const messages = data.split('\n').filter(Boolean);
        for (const message of messages) {
            await channel.send(message);

            // 發送對應的 K 線圖
            const symbol = message.split(' ')[1].replace(':', '');
            const imagePath = path.join('C:\\Users\\Rushia is boingboing\\Desktop\\tranding\\discord\\K highline', `${symbol}_Kline.png`);
            try {
                await fs.promises.access(imagePath, fs.constants.F_OK);
                await channel.send({ files: [imagePath] });
                console.log(`圖片已發送: ${imagePath}`);
            } catch (err) {
                console.error(`圖片不存在: ${imagePath}`);
            }
        }
        await channel.send('需要什麼再/owo 一下dayo');
    } catch (error) {
        console.error(`exec error: ${error}`);
    }
}
//每小時K線圖
async function executeHourlyTask(channel) {
    try {
        const { stdout } = await execPromise('python "C:\\Users\\Rushia is boingboing\\Desktop\\tranding\\github\\pybit-5.7.0\\examples\\K linetest.py"');
        const { Ethstdout } = await execPromise('python "C:\\Users\\Rushia is boingboing\\Desktop\\tranding\\github\\pybit-5.7.0\\examples\\EthKline.py"');
        // 發送輸出結果到 Discord 頻道
        await channel.send(`每小時任務輸出結果:`);
            await channel.send("BTC1小時K線圖");
            const imagePath = path.join('C:\\Users\\Rushia is boingboing\\Desktop\\tranding\\discord\\K line', `Klinetest.png`);
            try {
                await fs.promises.access(imagePath, fs.constants.F_OK);
                await channel.send({ files: [imagePath] });
                console.log(`圖片已發送: ${imagePath}`);
            } catch (err) {
                console.error(`圖片不存在: ${imagePath}`);
            }
            await channel.send("ETH1小時K線圖");
            const EthimagePath = path.join('C:\\Users\\Rushia is boingboing\\Desktop\\tranding\\discord\\K line', `EthKlinetest.png`);
            try {
                await fs.promises.access(EthimagePath, fs.constants.F_OK);
                await channel.send({ files: [EthimagePath] });
                console.log(`圖片已發送: ${EthimagePath}`);
            } catch (err) {
                console.error(`圖片不存在: ${EthimagePath}`);
            }
            await channel.send('需要什麼再/owo一下dayo');
    } catch (error) {
        console.error(`exec error: ${error}`);
    }
    
}
//每4小時K線圖
async function execute4HourlyTask(channel) {
    try {
        const { stdout } = await execPromise('python "C:\\Users\\Rushia is boingboing\\Desktop\\tranding\\github\\pybit-5.7.0\\examples\\BTC4H.py"');
        const { Ethstdout } = await execPromise('python "C:\\Users\\Rushia is boingboing\\Desktop\\tranding\\github\\pybit-5.7.0\\examples\\Eth4H.py"');
        // 發送輸出結果到 Discord 頻道
        await channel.send(`呼叫的4H圖呈上:dayo`);
            await channel.send("BTC4小時K線圖dayo");
            const imagePath = path.join('C:\\Users\\Rushia is boingboing\\Desktop\\tranding\\discord\\K4line', `Klinetest.png`);
            try {
                await fs.promises.access(imagePath, fs.constants.F_OK);
                await channel.send({ files: [imagePath] });
                console.log(`圖片已發送: ${imagePath}`);
            } catch (err) {
                console.error(`圖片不存在: ${imagePath}`);
            }
            await channel.send("ETH4小時K線圖dayo");
            const EthimagePath = path.join('C:\\Users\\Rushia is boingboing\\Desktop\\tranding\\discord\\K4line', `EthKlinetest.png`);
            try {
                await fs.promises.access(EthimagePath, fs.constants.F_OK);
                await channel.send({ files: [EthimagePath] });
                console.log(`圖片已發送: ${EthimagePath}`);
            } catch (err) {
                console.error(`圖片不存在: ${EthimagePath}`);
            }
            await channel.send('需要什麼再/owo一下dayo');
    } catch (error) {
        console.error(`exec error: ${error}`);
    }
    
}