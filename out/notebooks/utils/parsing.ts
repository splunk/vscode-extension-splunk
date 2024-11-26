/**
 * This helper function retrieves the names of all module-level search statements
 * 
 * @param spl2Module module contents
 * @returns array of regex matches of statements capturing names of each statement
 */
export function getModuleStatements(spl2Module: string): string[] {
    // Remove anything within comments, field literals, string
    // literals, or between braces { .. } which will eliminate
    // function/lambda params like `$it -> { $p = 1 }`
    // and commented-out statements like /* $out = from [{}] */
    let inBlockComment = false; // /* .. */
    let inField = false; // ' .. '
    let inString = false; // " .. "
    let inLineComment = false; // // .. <EOL>
    let braceLevel = 0; // { .. }
    
    let newModule = '';
    let prev = '';
    while (spl2Module.length > 0) {
        let indx = 0;
        let next = spl2Module.charAt(indx++);
        let peeked = peek(spl2Module);
        let crlf = (next === '\r' && peeked === '\n');
        let newLine = crlf || (next === '\n');
        if (inBlockComment) {
            if (next === '*' && peeked === '/') {
                inBlockComment = false; // exit block comment
                indx++; // move past */
            }
        } else if (inField) {
            if (next === '\'' && prev !== '\\') { // ignore \'
                inField = false; // exit field literal
            }
        } else if (inString) {
            if (newLine || (next === '"' && prev !== '\\')) { // ignore \"
                inString = false; // exit string literal
                if (crlf) {
                    indx++; // move past \r\n
                }
            }
        } else if (inLineComment) {
            if (newLine) {
                inLineComment = false; // exit line comment
                if (crlf) {
                    indx++; // move past \r\n
                }
            }
        } else if (braceLevel > 0) {
            if (next === '{') {
                braceLevel++;
            } else if (next === '}') {
                braceLevel--;
            }
            if (braceLevel === 0) {
                // insert newlines after blocks like function and dataset declarations
                // to start new statements/declarations on new lines when possible
                newModule += '\n';
            }
        } else {
            // Check for entering new block
            switch (next) {
                case '/':
                    if (peeked === '/') {
                        inLineComment = true;
                        indx++; // move past //
                    } else if (peeked === '*') {
                        inBlockComment = true;
                        indx++; // move past /*
                    }
                    break;
                case '\'':
                    inField = true;
                    break;
                case '"':
                    inString = true;
                    break;
                case '{':
                    braceLevel++;
                    break;
            }
            // if we're not in one of the blocks above, write to cleaned module
            if (!inBlockComment && !inField && !inString && !inLineComment && braceLevel === 0) {
                newModule += next;
            }
        }
        spl2Module = spl2Module.substring(indx, spl2Module.length);
    }
    
    // Match anything that looks like `$statement_1 = ...` and return the statement names
    return [...newModule.matchAll(/^\s*\$([a-zA-Z0-9_]+)[\s]*=/gm)]
        .map(group => (group.length > 1) ? group[1] : null)
        .filter(val => (val !== null));
}

function peek(str: string): string {
    return (str.length > 1) ? str.charAt(1) : "";
}