
const fs = require('fs');
const vm = require('vm');

try {
    const inputData = JSON.parse(fs.readFileSync('_hic_js_in.json', 'utf8'));
    const context = vm.createContext(inputData);
    
    // User code
    const userCode = `

console.log("Inside Node.js:");
console.log("Original value: " + value);
value = value * 2;
var js_result = "Hello from JS";

`;
    
    vm.runInContext(userCode, context);
    
    // Write output
    fs.writeFileSync('_hic_js_out.json', JSON.stringify(context));
} catch (e) {
    console.error('JS Error:', e);
    process.exit(1);
}
