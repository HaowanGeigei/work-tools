import requests
import json
import time
import subprocess
import re
import argparse


MODEL = 'gpt-4-0613'

# Define patterns to exclude (e.g., test directories)
exclude_patterns = [r'^tests/', r'^test/']

token = None

current_line = 0

def setup():
    resp = requests.post('https://github.com/login/device/code', headers={
            'accept': 'application/json',
            'editor-version': 'Neovim/0.6.1',
            'editor-plugin-version': 'copilot.vim/1.16.0',
            'content-type': 'application/json',
            'user-agent': 'GithubCopilot/1.155.0',
            'accept-encoding': 'gzip,deflate,br'
        }, data='{"client_id":"Iv1.b507a08c87ecfe98","scope":"read:user"}')


    # Parse the response json, isolating the device_code, user_code, and verification_uri
    resp_json = resp.json()
    device_code = resp_json.get('device_code')
    user_code = resp_json.get('user_code')
    verification_uri = resp_json.get('verification_uri')

    # Print the user code and verification uri
    print(f'Please visit {verification_uri} and enter code {user_code} to authenticate.')


    while True:
        time.sleep(5)
        resp = requests.post('https://github.com/login/oauth/access_token', headers={
            'accept': 'application/json',
            'editor-version': 'Neovim/0.6.1',
            'editor-plugin-version': 'copilot.vim/1.16.0',
            'content-type': 'application/json',
            'user-agent': 'GithubCopilot/1.155.0',
            'accept-encoding': 'gzip,deflate,br'
            }, data=f'{{"client_id":"Iv1.b507a08c87ecfe98","device_code":"{device_code}","grant_type":"urn:ietf:params:oauth:grant-type:device_code"}}')

        # Parse the response json, isolating the access_token
        resp_json = resp.json()
        access_token = resp_json.get('access_token')

        if access_token:
            break

    # Save the access token to a file
    with open('.copilot_token', 'w') as f:
        f.write(access_token)

    print('Authentication success!')


def get_token():
    global token
    global current_line
        # Check if the .copilot_token file exists
    while True:
        try:
            with open('.copilot_token', 'r') as f:
                lines = f.readlines()
                total_lines = len(lines)
                # Use modulo to cycle through the lines
                access_token = lines[current_line % total_lines].strip()
                current_line += 1
                break
        except FileNotFoundError:
            setup()
    # Get a session with the access token
    resp = requests.get('https://api.github.com/copilot_internal/v2/token', headers={
        'authorization': f'token {access_token}',
        'editor-version': 'Neovim/0.6.1',
        'editor-plugin-version': 'copilot.vim/1.16.0',
        'user-agent': 'GithubCopilot/1.155.0'
    })

    # Parse the response json, isolating the token
    resp_json = resp.json()
    token = resp_json.get('token')

def chat(message):
    global token
    # If the token is None, get a new one
    # if token is None:
    get_token()
    messages = []

    messages.append({
        "content": str(message),
        "role": "user"
    })    
    
    try:
        resp = requests.post('https://api.githubcopilot.com/chat/completions', headers={
                'authorization': f'Bearer {token}',
                'Editor-Version': 'vscode/1.80.1',
            }, json={
                'intent': False,
                'model': MODEL,
                'temperature': 0,
                'top_p': 1,
                'n': 1,
                'stream': True,
                'messages': messages
            })
    except requests.exceptions.ConnectionError:
        return ''

    result = ''

    # Parse the response text, splitting it by newlines
    resp_text = resp.text.split('\n')
    for line in resp_text:
        # If the line contains a completion, print it
        if line.startswith('data: {'):
            # Parse the completion from the line as json
            json_completion = json.loads(line[6:])
            try:
                completion = json_completion.get('choices')[0].get('delta').get('content')
                if completion:
                    result += completion
                else:
                    result += '\n'
            except:
                pass

    messages.append({
        "content": result,
        "role": "assistant"
    })
    
    if result == '':
        print(resp.status_code)
        print(resp.text)

    # import time
    # # Sleep for 10 seconds
    # time.sleep(10)
    return result


import subprocess
def run_cmd(command):
    try:
        # 执行命令并捕获输出和错误
        result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        print(result.stdout)
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Command '{command}' failed with return code {e.returncode}")
        print("Error output:\n", e.stderr)
        return None


def remove_unittest_from_gitdiff(diff_content):
    filtered_lines = []
    skip = False

    for line in diff_content.splitlines():
        # 检查是否遇到测试代码的 diff --git 行
        if line.startswith('diff --git') and 'test/' in line:
            skip = True
        if not skip:
            filtered_lines.append(line)

    return '\n'.join(filtered_lines)


from urllib.parse import urlparse, parse_qs


def parse_github_pr_url(url):
    # 解析URL
    parsed_url = urlparse(url)

    # 检查URL路径是否符合预期格式
    path_parts = parsed_url.path.strip('/').split('/')
    if len(path_parts) >= 4 and path_parts[2] == 'pull':
        repo = f"{path_parts[0]}/{path_parts[1]}"
        pr_id = path_parts[3]
        return parsed_url.hostname, repo, pr_id
    else:
        raise ValueError("Invalid GitHub PR URL format")


def main():
    # get the url from command line argument
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--prUrl', required=True, 
                        help='PR url e.g. https://git.autodesk.com/WIPDM/wip-dm-service/pull/4542', default=None)
    parser.add_argument('-o', '--output', required=True, help='output file' , default="output.md")
    args = parser.parse_args()

    output_file = args.output
    url = args.prUrl

    host_name, repo_name, pr_id = parse_github_pr_url(url)
    repo = "{}/{}".format(host_name, repo_name)
    # print(f"Repository: {repo}")
    # print(f"PR ID: {pr_id}")

    #"gh", "pr", "view", String.valueOf(prid), "--repo", repo, "--json", "title,body"
    command = "gh pr view "+pr_id+" --repo "+repo+" --json title"
    git_title = run_cmd(command)
    # print(git_title)

    #"gh", "pr", "view", String.valueOf(prid), "--repo", repo, "--json", "title,body"
    command = "gh pr view "+pr_id+" --repo "+repo+" --json body"
    git_body = run_cmd(command)
    # print(git_body)

    command = "gh pr diff "+pr_id+" --repo "+repo
    git_diff_all = run_cmd(command)
    # print(git_diff)
    # remove test cases
    git_diff = remove_unittest_from_gitdiff(git_diff_all)


    # 定义 prompt
    common_prompt = \
        (f"Your task is to review the following Git pull request (PR) and provide suggestions for improvement including code examples in form of comparisons."
               f"Focus on new PR code (lines starting with '+')"
               f"Keep in mind that PR description may be partial, simplistic, non-informative or out of date. Hence, compare them to the PR diff code, and use them only as a reference.\n")
    content = f"\n\nTitle:\n{git_title}\n\nBody:\n{git_body}\n\nDiff:\n{git_diff}"

    prompt0 = (common_prompt+
                content)
    result0 = chat(prompt0)
    # print('-----------------------------------------------------------------------------------------------------------------------------------------')
    # print(result0)
    print("Computing prompt1")
    prompt1 = (common_prompt+
                "Pay more attention to logic error, naming, initialization/destruction, logic simplification, syntax modernization, readability, consistency, error handling and code duplication"+
                content)
    result1 = chat(prompt1)
    # print('-----------------------------------------------------------------------------------------------------------------------------------------')
    # print(result1)

    print("Computing prompt2")
    prompt2 = (common_prompt+
                "Find code smell, feature envy and violation of best practice or design principles"+
                content)
    result2 = chat(prompt2)
    # print('-----------------------------------------------------------------------------------------------------------------------------------------')
    # print(result2)

    print("Computing prompt3")
    prompt3 = (common_prompt+
                "Provide improvement suggestion on software design, refactoring, performance and security"+
                content)
    result3 = chat(prompt3)
    # print('-----------------------------------------------------------------------------------------------------------------------------------------')
    # print(result3)

    print("Computing prompt4")
    prompt = (common_prompt+
               "ChatGPT, could you please review the code based on the suggestions provided and offer a corrected version of the code? Focus on suggestions rather than correct code."
               +"\n"+result0+result1+result2+result3+
                content)
    result = chat(prompt)
    print('------------------------final result-----------------------------------------------------------------------------------------------------------------')
    print(result)

    # output the result to a markdown file    
    with open(output_file, "w") as f:
        f.write(result)


if __name__ == '__main__':
    main()