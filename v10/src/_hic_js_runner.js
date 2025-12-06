
const fs = require('fs');
const vm = require('vm');

try {
    const inputData = JSON.parse(fs.readFileSync('_hic_js_in.json', 'utf8'));
    const context = vm.createContext(inputData);
    
    // User code
    const userCode = `

// Use functional JS methods
var sum = data.reduce((a, b) => a + b, 0);
data.push(sum);

`;
    
    vm.runInContext(userCode, context);
    
    // Write output
    fs.writeFileSync('_hic_js_out.json', JSON.stringify(context));
} catch (e) {
    console.error('JS Error:', e);
    process.exit(1);
}
