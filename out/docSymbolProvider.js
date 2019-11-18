"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const vscode = require("vscode");

class confDocumentSymbolProvider {
    provideDocumentSymbols(document, token) {
        const result = [];

        const sectionRegex = /^\s*\[([^\]]+)\]/;
        const keyRegex = /^\s*([^\[;=]+)\s*=/;

        let prevSecName = null;
        let prevSecRangeStart = null;
        let prevSecRangeEnd = null;
        
        for (let line = 0; line < document.lineCount; line++) {
            const { text } = document.lineAt(line);

            const secMatched = text.match(sectionRegex);
            if (secMatched) {

                if (prevSecName != null)
                {
                    prevSecRangeEnd = new vscode.Position(line, 0);
                    
                    const secLoc = new vscode.Location(document.uri, new vscode.Range(prevSecRangeStart, prevSecRangeEnd));
                    const prevSectionSymbol = new vscode.SymbolInformation(prevSecName, vscode.SymbolKind.Class, '', secLoc);
                    result.push(prevSectionSymbol);
                }

                prevSecName = secMatched[1];
                prevSecRangeStart = new vscode.Position(line, 0);
                continue;
            }

            const keyMatched = text.match(keyRegex);
            if((prevSecName != null) && keyMatched){
                const keyLoc = new vscode.Location(document.uri, new vscode.Position(line, 0));
                result.push(new vscode.SymbolInformation(keyMatched[1], vscode.SymbolKind.Function, prevSecName, keyLoc));    
                continue;
            }
        }

        if (prevSecName != null)
        {
            prevSecRangeEnd = new vscode.Position(document.lineCount -1 , 0);
            const secLoc = new vscode.Location(document.uri, new vscode.Range(prevSecRangeStart, prevSecRangeEnd));
            const prevSectionSymbol = new vscode.SymbolInformation(prevSecName, vscode.SymbolKind.Class, '', secLoc);
            result.push(prevSectionSymbol);
        }

        return result;
    }
}
exports.confDocumentSymbolProvider = confDocumentSymbolProvider;
//# sourceMappingURL=docSymbolProvider.js.map