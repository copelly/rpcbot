const { Client, RichPresence } = require("discord.js-selfbot-v13");
const fs = require("fs");
const path = require("path");

const configPath = path.join(__dirname, "config.json");
let config = { tokens: [] };
try {
    config = require(configPath);
} catch (e) {
    console.warn("config.json을 불러오는 중 오류 발생, 빈 토큰 목록으로 시작합니다.");
}

const tokens = Array.isArray(config.tokens) ? config.tokens : [];
const clients = [];

function startClient(tokenData) {
    const client = new Client();

    client.on("ready", async () => {
        console.log(`${client.user.username} is ready!`);

        const currentDate = new Date();
        const expirationDate = new Date(tokenData.day);

        if (expirationDate < currentDate) {
            console.log(`Expiration date (${tokenData.day}) has passed for ${client.user.username}. Skipping...`);
            return;
        }

        const r = new RichPresence()
            .setApplicationId("817229550684471297")
            .setType(tokenData.type)
            .setState(tokenData.state)
            .setName(tokenData.name)
            .setDetails(tokenData.details)
            .setStartTimestamp(Date.now());

        try {
            r.setAssetsLargeImage(tokenData.largeimage);
            r.setAssetsLargeText(tokenData.largete);
        } catch (error) {
            console.error(`Error setting large image for ${client.user.username}: ${error.message}`);
        }

        try {
            r.setAssetsSmallImage(tokenData.smallimage);
            r.setAssetsSmallText(tokenData.smallte);
        } catch (error) {
            console.error(`Error setting small image for ${client.user.username}: ${error.message}`);
        }

        if (tokenData.button1 && tokenData.button1link) {
            r.addButton(tokenData.button1, tokenData.button1link);
        }
        if (tokenData.button2 && tokenData.button2link) {
            r.addButton(tokenData.button2, tokenData.button2link);
        }

        try {
            client.user.setActivity(r);
        } catch (error) {
            console.error(`Error setting activity for ${client.user.username}: ${error.message}`);
        }
    });

    client.on('error', error => {
        console.error(`Error occurred with token ${tokenData.token}: ${error.message}`);
    });

    client.login(tokenData.token).catch(error => {
        console.error(`Error logging in with token ${tokenData.token}: ${error.message}`);
    });

    return client;
}

const activeTokens = tokens.filter(t => t && t.active);
if (activeTokens.length === 0) {
    console.log("실행 가능한 활성 토큰이 없습니다.");
} else {
    activeTokens.forEach(td => {
        clients.push(startClient(td));
    });

    Promise.all(clients.map(client => {
        return new Promise((resolve, reject) => {
            client.once('ready', resolve);
            client.once('error', reject);
        });
    })).then(() => {
        console.log("모든 클라이언트가 준비되었습니다.");
    }).catch(err => {
        console.error("클라이언트 시작 중 오류:", err);
    });
}
