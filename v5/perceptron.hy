/*
    https://www.w3schools.com/ai/ai_perceptrons.asp

    const threshold = 1.5;
    const inputs = [1, 0, 1, 0, 1];
    const weights = [0.7, 0.6, 0.5, 0.3, 0.4];

    let sum = 0;
    for (let i = 0; i < inputs.length; i++) {
    sum += inputs[i] * weights[i];
    }

    const activate = (sum > 1.5);
*/

float threshold = 1.5;
int inputs[5] = [1, 0, 1, 0, 1];
float weights[5] = [0.7, 0.6, 0.5, 0.3, 0.4];

float sum = 0.0;

for(int i = 0; i < 5; i = i + 1){
    sum = sum + inputs[i] * weights[i];
}

bool activate = (sum > 1.5);
print(activate); // Output: true