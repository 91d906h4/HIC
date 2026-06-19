/*
    A single perceptron: weighted sum of inputs compared to a threshold.
    https://www.w3schools.com/ai/ai_perceptrons.asp
*/

float threshold = 1.5;
int inputs[5] = [1, 0, 1, 0, 1];
float weights[5] = [0.7, 0.6, 0.5, 0.3, 0.4];

float sum = 0.0;
for(int i = 0; i < 5; i = i + 1){
    sum = sum + inputs[i] * weights[i];
}

bool activate = sum > threshold;
print(activate);   // true
