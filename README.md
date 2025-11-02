## Disclaimer: This is Alpha Software
Ginny depends on third party software and uses LLMs to generate code that will be run and tested on your terminal! Handle with care. I suggest you run Ginny in a [virtual environment](#creating-a-virtual-environment)

## Introducing Ginny!
Ginny is a CLI tool that leverages LLMs to generate code according to the specifications given to her!

For now, we've tested Ginny on introductory programming assignments in C handed to undergraduate students in [DIT - UoA](https://www.di.uoa.gr/en) (All the inputs used for testing can be found in the `test_cases` directory).

Given a `specifications.pdf` Ginny will attempt to create an implementation that fulfils the specifications.

Ginny then will:
+ 📖 Read the contents of the PDF
+ 🧪 Extract the test cases and other relevant specifications
+ 🛠️ Attempt to implement a solution
+ 🔁 Iterate on the implementation until it passes [the desired percentage](#--acc) of test cases

## How to install Ginny

### Pre-requisites:
* You'll need Python installed and Poetry to install the third party dependencies.

* Ginny invokes chat-based LLMs during execution. For that reason you'll need an API Key. For now Anthropic's, OpenAI's and Google's models are supported. Depending on which one you want to use you'll have to export the relevant key in your environment using:

```
// to use Anthropic's models
export ANTHROPIC_API_KEY=your-key-here

// to use OpenAI's models
export OPENAI_API_KEY=your-key-here or

// to use Google's models
export GOOGLE_API_KEY=your-key-here
```

### Installation
Clone the repostitory locally by running the following command:
```
git clone git@github.com:stavros-mhs/ginny
```

### Creating a Virtual Environment
I recommend using Ginny in a virtual environment. Firstly `cd ginny` to move to the cloned repository. The easiet way is to create a python virtual environment by running:
```
python3 -m venv venv
```
and activate it using:
```
. ./venv/bin/activate
```
Dependencies are handled by poetry so if you don't have it, install it using pip by running: `pip install poetry` and finally run: `poetry install`.

## How to use Ginny

To use Ginny you run:

`ginny solve /path/to/pdf/input.pdf --model="model-name"`

### How an input should be structured for best use

Ginny is given inputs in the form of PDF files. The input should contain:

+ Some context on the problem Ginny will attempt to solve.
+ Specifications on how a solution should look like (what inputs the deliverable has to handle, on what range of inputs it should work, when to exit, how the code should be compiled etc.).
+ Test cases that will be used for validation.
+ Optional:
	+ Some code showcasing inteded behavior

### Other parameters

#### `--acc`

The most important parameter is `--acc=desired_accuracy`. Accuracy is defined as:

$$
\frac{\text {\# of tests passed}}{\text {\# of tests}}
$$

Accuracy is a float number. By default, accuracy is set to 1, meaning all test cases must pass for an implemetation to pass. If you want to be less austere you can lower it to some other fraction but - keep in mind that an implementation that passed with `acc < 1` will most likely fail on some test cases!

#### `--model`

This is how you choose a model. Models that start with "claude-", "gemini-" or "gpt-" are supported.

#### `--iter`

Expects an integer. Maximum number of attempts to create a succesful implementation. By default it's set to 10.

#### `--SubprocessTimeout`

Maximum time (in seconds) for Ginny's code to run when testing an implementation before failing the test case. You may want to up/lower it depedning on what you want Ginny to solve (i.e. if you ask Ginny to make a factoring algorithm and one test case is a 40 digit number, you probably don't want testing to take 15 minutes before failing and trying again).

Expects integer value. By default it's set to 30 (seconds).

#### `--APItimeout`

Maximum time (in seconds) allowed to wait for API response. If the limit is exceeded it'll raise an APITimeoutError.

Expects integer value. By default it's set to 300 (seconds = 5 minutes)

## Tips

1. The more descriptive the specifications document the better from empirical testing.

2. If a certain model inconsistently solves a problem in 10 iterations, upgrading the model usually makes the output more consistent and yields better results than upping the iteration limit.
