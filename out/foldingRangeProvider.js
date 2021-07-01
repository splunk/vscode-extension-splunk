"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const vscode = require("vscode");

class confFoldingRangeProvider {
    provideFoldingRanges(document, foldingContext, token) {
        const result = [];

        const sectionRegex = /^\s*\[([^\]]+)\]/;
        const keyRegex = /^\s*([^\[;=]+)\s*=/;

        let prevSecName = null;
        let prevSecLineStart = null;
        let prevSecLineEnd = null;
        let lastKeyLine = null;
        
        for (let line = 0; line < document.lineCount; line++) {
            const { text } = document.lineAt(line);

            const secMatched = text.match(sectionRegex);
            if (secMatched) {

                if (prevSecName != null)
                {
                    prevSecLineEnd = lastKeyLine;
                    const prevSecFoldingRange = new vscode.FoldingRange(prevSecLineStart, prevSecLineEnd, vscode.FoldingRangeKind.Region);
                    result.push(prevSecFoldingRange);
                }

                prevSecName = secMatched[1];
                prevSecLineStart = line;
                continue;
            }

            const keyMatched = text.match(keyRegex);
            if((prevSecName != null) && keyMatched){
                lastKeyLine = line;   
                continue;
            }
        }

        if (prevSecName != null)
        {
            prevSecLineEnd = document.lineCount - 1;
            const prevSecFoldingRange = new vscode.FoldingRange(prevSecLineStart, prevSecLineEnd, vscode.FoldingRangeKind.Region);
            result.push(prevSecFoldingRange);
        }

        return result;
    }
}

exports.confFoldingRangeProvider = confFoldingRangeProvider;