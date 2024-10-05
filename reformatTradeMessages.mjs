import logger from "./logger.mjs";

const currencies = {
    'AUDCAD': 'AUDCAD',
    'AUDCHF': 'AUDCHF',
    'AUDJPY': 'AUDJPY',
    'AUDNZD': 'AUDNZD',
    'AUDUSD': 'AUDUSD',
    'BTC.USD': 'BTCUSD',
    'BTC/USD' : 'BTCUSD',
    'BTCUSD': 'BTCUSD',
    'CAC40' : 'CAC40',
    'CADCHF': 'CADCHF',
    'CHFEUR': 'CHFEUR',
    'Chfjpy': 'CHFJPY',
    'DAX30' : 'DAX30',
    'DXY': 'DXY',
    'EURAUD': 'EURAUD',
    'EURCAD': 'EURCAD',
    'EURCHF': 'EURCHF',
    'EURGBP': 'EURGBP',
    'EURJPY': 'EURJPY',
    'EURNZD': 'EURNZD',
    'EURUSD': 'EURUSD',
    'GBPAUD': 'GBPAUD',
    'GBPCAD': 'GBPCAD',
    'GBPJPY': 'GBPJPY',
    'GBPNZD': 'GBPNZD',
    'GBPUSD': 'GBPUSD',
    'Gold': 'XAUUSD',
    'GOLD': 'XAUUSD',
    'NAS100': 'NASDAQ100',
    'NASDAQ100': 'NASDAQ100',
    'NZDCAD': 'NZDCAD',
    'NZDCHF': 'NZDCHF',
    'NZDJPY': 'NZDJPY',
    'NZDUSD': 'NZDUSD',
    'SP500' : 'SP500',
    'US30': 'DJ30',
    'USDCAD': 'USDCAD',
    'USDCHF': 'USDCHF',
    'USDJPY': 'USDJPY',
    'XAGUSD': 'XAGUSD',
    'XAU.USD': 'XAUUSD',
    'XAUUSD': 'XAUUSD',
    'USOIL': 'USOIL',
    'XAU/USD': 'XAUUSD'
}

function getCurrency(message){
    // Attempt to match the beginning of the message with any currency key
    for (const currencyKey in currencies) {
        if (message.includes(currencyKey)) {
            return currencyKey;
        }
    }

    return null
}

export function extractCurrency(message) {
    // Attempt to match the beginning of the message with any currency key
    for (const currencyKey in currencies) {
        if (message.includes(currencyKey)) {
            return currencies[currencyKey];
        }
    }

    let error = new Error('No currency found.');

    logger.error(error)

    throw error;
}

export function cleanMessage(message) {
    // Remove all new lines and replace them with spaces to prevent word concatenation
    let cleanedMessage = message.replace(/\r?\n|\r/g, ' ');

    // Convert the entire message to uppercase
    cleanedMessage = cleanedMessage.toUpperCase();

    // Normalize the message to decompose certain stylized characters
    cleanedMessage = cleanedMessage.normalize("NFKD");

    // Optional: Remove non-ASCII characters if the normalization doesn't convert stylized text to ASCII
    cleanedMessage = cleanedMessage.replace(/[^\x00-\x7F]/g, "");

    // Remove all hash symbols
    cleanedMessage = cleanedMessage.replace(/#/g, '');

    // Remove all colons
    cleanedMessage = cleanedMessage.replace(/:/g, '');

    // Remove all dots that are not part of a decimal number
    // This involves keeping dots that are between two digits
    cleanedMessage = cleanedMessage.replace(/(\D)\.|\.\D/g, '$1');

    // Replace "TAKE PROFIT" with "TP" and "STOP LOSS" with "SL"
    cleanedMessage = cleanedMessage.replace(/TAKE PROFIT/g, 'TP').replace(/STOP LOSS/g, 'SL');

    cleanedMessage = cleanedMessage.replace(/TP\s?\d\s/g, 'TP ');

    cleanedMessage = cleanedMessage.replace(/@/g, '');

    // Remove extra spaces (including those potentially introduced by removing symbols)
    // This is done by replacing multiple spaces with a single space
    cleanedMessage = cleanedMessage.replace(/\s+/g, ' ');


    return cleanedMessage.trim();
}


export function extractProfit(message) {
    const tpPattern = /TP (\d+\.?\d*)/g; // Matches "TP" followed by a space and then a number
    let matches;
    const profits = [];

    // Use a loop to extract all matches of the TP pattern from the message
    while ((matches = tpPattern.exec(message)) !== null) {
        // Parse the number from the match and push it to the profits array
        profits.push(parseFloat(matches[1]));
    }

    return profits;
}

export function extractLoss(message) {
    const slPattern = /SL (\d+\.?\d*)/; // Matches "SL" followed by a space and then a number
    const match = message.match(slPattern);

    if (match) {
        return parseFloat(match[1]);
    }

    let error = new Error('No stop loss found');

    logger.error(error)

    throw error;
}

export function extractCommand(message) {
    const upperMessage = message.toUpperCase();

    // Check for "BUY" or "SELL" and "NOW" separately
    const hasBuy = upperMessage.includes("BUY");
    const hasSell = upperMessage.includes("SELL");
    const hasNow = upperMessage.includes("NOW");

    // Determine command based on what was found
    if (hasSell && hasNow) {
        return "SELL";
    } else if (hasBuy && hasNow) {
        return "BUY";
    } else if (hasSell) {
        return "SELL";
    } else if (hasBuy) {
        return "BUY";
    }

    let error = new Error("No trading command found");

    logger.error(error)

    throw error;
}

export function extractTradeValue(message) {
    // Use previously defined functions to extract and remove known parts of the message
    const symbol = getCurrency(message);
    const command = extractCommand(message);
    const profits = extractProfit(message); // Assuming this returns an array of TP values
    const loss = extractLoss(message);

    // Remove the extracted parts from the message
    let cleanedMessage = message.replace(symbol, '')
        .replace(new RegExp(`SL ${loss}`, 'gi'), '');

    // Remove TP values
    command.split(' ').forEach((text) => {
        cleanedMessage = cleanedMessage.replace(text, '')
    })

    // Remove TP values more flexibly
    profits.forEach(profit => {
        // Remove the profit value, accounting for potential formatting differences
        let profitRegex = new RegExp(`TP ${profit.toString().replace('.', '\\.')}`, 'gi');
        cleanedMessage = cleanedMessage.replace(profitRegex, '');
        // Attempt to remove trailing .00 parts if they become isolated
        cleanedMessage = cleanedMessage.replace(/\.00\b/g, '');
    });
    //
    // Clean up any remaining identifiers and whitespace to isolate the trade value/range
    cleanedMessage = cleanedMessage.replace(/[^\d\.\/\s-]/g, '').trim();

    logger.info('Detecting action value/range: ' + cleanedMessage)

    // Assuming the trade values or range are now leading the cleaned message,
    // split by space, slash, or dash to account for different range formats
    let potentialRange = cleanedMessage.split(/\s+|[-\/]/).map(Number).filter(Boolean);

    // Determine and return the appropriate format based on the extracted numbers
    if (potentialRange.length > 1) {
        // Return as range if more than one number is found
        return potentialRange.slice(0, 2); // Take only the first two numbers for the range
    } else if (potentialRange.length === 1) {
        // Return a single number if only one is found
        return potentialRange[0];
    }

    let error = new Error("No trade value or range found");
    logger.error(error)
    throw error;
}

export function extractActions(message) {
    const cleanedMessage = cleanMessage(message)

    logger.info(`Cleaned: ${cleanedMessage}`)

    const symbol = extractCurrency(cleanedMessage)
    const actionType = extractCommand(cleanedMessage);
    const profits = extractProfit(cleanedMessage); // Assuming this returns an array of TP values
    const stopLoss = extractLoss(cleanedMessage);
    const entry = extractTradeValue(cleanedMessage)

    return profits.map(takeProfit => ({
        entry,
        symbol,
        actionType,
        takeProfit,
        stopLoss
    }))
}

export default function reformatTradeMessages(message) {
    return extractActions(message)
}

// Read input from stdin
process.stdin.setEncoding('utf8');
let input = '';

process.stdin.on('data', (chunk) => {
    input += chunk;
});

process.stdin.on('end', () => {
    const result = reformatTradeMessages(input);
    console.log(JSON.stringify(result));
});