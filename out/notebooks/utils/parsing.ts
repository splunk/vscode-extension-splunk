export function getModuleStatements(spl2Module: string) {
    return [...spl2Module.matchAll(/^\s*\$([a-zA-Z0-9_]+)[\s]*=/gm)]
}