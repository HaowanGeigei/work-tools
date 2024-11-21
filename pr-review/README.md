
# Prerequisite
You need to have a GitHub Copilot account.

# Steps to Review a Pull Request

1. Run the `copilot_review_pr.py` script. The script requires two arguments: the URL of the PR and the output file path.
    ```sh
    python3 copilot_review_pr.py -u https://github.com/UpchainXLM/monolith-java/pull/10784  -o C:\Users\wanh\Downloads\out.md
    ```

    ```sh
    python3 ./copilot_review_pr.py -u https://git.autodesk.com/WIPDM/wip-dm-service/pull/4688 -o /Users/kurnias/source/wip-tools/pr-review/out2.md
    ```

2. On the first run, you will be prompted to authenticate:
    ```
    Please visit https://github.com/login/device and enter code 0624-CFB0 to authenticate.
    ```
    Login to GitHub using the provided code.

3. The output will be saved to the specified output file. For the best viewing experience, it is recommended to output to a markdown file and view the result using a markdown viewer.
Sample output:  https://github.com/HaowanGeigei/work-tools/blob/main/pr-review/out.md




Thanks contributions from @zhu-junyi and @kurnias
