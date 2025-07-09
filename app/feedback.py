import FreeSimpleGUI as sg
from datetime import datetime
import os
from . import keystore as key
import github
import traceback
from github import Github

def generate_feedback_screen():
    layout = [

        [sg.HorizontalSeparator()],
        [
            sg.Text(
                'Feedback Form', 
                font=('Helvetica', 16, 'bold'), 
                pad=((0, 0), (0, 0))
            )
        ],
        [sg.HorizontalSeparator()],
        [
            sg.Text('Feedback Type:', font=('Helvetica', 12, 'bold'), pad=((0, 0), (10, 5))),
        ],
        [
            sg.Radio('Bug Report', 'feedback_type', key='-BUG-', font=('Helvetica', 11)),
            sg.Radio('Feature Request', 'feedback_type', key='-FEATURE-', font=('Helvetica', 11)),
            sg.Radio('General Feedback', 'feedback_type', key='-GENERAL-', default=True, font=('Helvetica', 11)),
            sg.Radio('Other', 'feedback_type', key='-OTHER-', font=('Helvetica', 11))
        ],
                [
            sg.Text('Title/Issue:', font=('Helvetica', 12, 'bold'), pad=((0, 0), (10, 5))),
        ],
        [
            sg.Input(
                key='-TITLE-',
                size=(50, 1),
                font=('Helvetica', 11),
                default_text='Please describe the issue...',
                pad=((0, 0), (0, 10))
            )
        ],
        [
            sg.Text('Detailed Description:', font=('Helvetica', 12, 'bold'), pad=((0, 0), (10, 5))),
        ],
        [
            sg.Multiline(
                key='-DESCRIPTION-',
                size=(55, 8),
                font=('Helvetica', 11),
                default_text='Please provide detailed information about your feedback, issue, or suggestion...',
                pad=((0, 0), (0, 10))
            )
        ],
        [
            sg.Text('Contact Information (Optional):', font=('Helvetica', 12, 'bold'), pad=((0, 0), (10, 5))),
        ],
        [
            sg.Text('Email:', font=('Helvetica', 11)),
            sg.Input(
                key='-EMAIL-',
                size=(30, 1),
                font=('Helvetica', 11),
                default_text='your.email@example.com',
                pad=((10, 0), (0, 10))
            )
        ],
        [
            sg.Text('Name:', font=('Helvetica', 11)),
            sg.Input(
                key='-USERNAME-',
                size=(30, 1),
                font=('Helvetica', 11),
                default_text='Your name (optional)',
                pad=((10, 0), (0, 10))
            )
        ],
        [sg.HorizontalSeparator()],
        [
            sg.Button(
                'Submit Feedback',
                key='-SUBMIT-',
                size=(15, 1),
                font=('Helvetica', 12, 'bold'),
                button_color=('white', 'green'),
                pad=((0, 10), (10, 0))
            ),
            sg.Button(
                'Clear Form',
                key='-CLEAR-',
                size=(12, 1),
                font=('Helvetica', 11),
                button_color=('white', 'orange'),
                pad=((0, 10), (10, 0))
            ),
            sg.Button(
                'Cancel',
                key='-CANCEL-',
                size=(10, 1),
                font=('Helvetica', 11),
                button_color=('white', 'red'),
                pad=((0, 0), (10, 0))
            )
        ]
    ]

    return layout

def feedback_screen():
    status = False

    # Get current date and time
    current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Define the feedback window layout
    layout = generate_feedback_screen()
    
    # Create the feedback window
    feedback_window = sg.Window(
        'Feedback Form',
        layout,
        keep_on_top=True,
        finalize=True,
        size=(600, 600),
        location=(100, 100)
    )
    
    # Event loop for the feedback window
    while True:
        event, values = feedback_window.read()
        
        if event in (sg.WIN_CLOSED, '-CANCEL-'):
            feedback_window.close()
            return status
            
        elif event == '-CLEAR-':
            # Clear all input fields
            feedback_window['-TITLE-'].update('')
            feedback_window['-DESCRIPTION-'].update('')
            feedback_window['-EMAIL-'].update('')
            feedback_window['-USERNAME-'].update('')
            feedback_window['-GENERAL-'].update(True)
            
        elif event == '-SUBMIT-':
            # Validate required fields
            title = values.get('-TITLE-', '').strip()
            description = values.get('-DESCRIPTION-', '').strip()
            
            if not title:
                sg.popup_error('Please enter a title/issue for your feedback.', title='Validation Error')
                continue
                
            if not description:
                sg.popup_error('Please provide a detailed description.', title='Validation Error')
                continue
            
            # Determine feedback type
            feedback_type = 'General Feedback'
            if values.get('-BUG-'):
                feedback_type = 'Bug Report'
            elif values.get('-FEATURE-'):
                feedback_type = 'Feature Request'
            elif values.get('-OTHER-'):
                feedback_type = 'Other'
   
            email = values.get('-EMAIL-', '').strip()
            user_name = values.get('-NAME-', '').strip()
            # Save feedback to file
            try:
                submit_report(
                    current_date, 
                    title, feedback_type, 
                    description, 
                    email, 
                    user_name
                )
                  
                sg.popup_ok(
                    'Thank you for your feedback!\n\nYour submission has been recorded successfully.',
                    title='Feedback Submitted',
                    font=('Helvetica', 12)
                )
                feedback_window.close()
                status = True
                return status
            except Exception as e:
                sg.popup_error(f'Error saving feedback: {str(e)}', title='Error')
                return status

def submit_report(current_date, title, feedback_type, description, email, user_name):
    file_log = 'app/assets/logs/feedback.log'
    create_feedback_to_log(current_date, title, feedback_type, description,email,user_name, file_log)

def create_feedback_to_log(current_date, title, feedback_type, description, email, user_name, file_log):
    
    # Make sure the directory exists
    os.makedirs(os.path.dirname(file_log), exist_ok=True)

    log_entry = (
        f"## {title}\n"
        f"Date      : {current_date}\n"
        f"User      : {user_name}\n"
        f"Email     : {email}\n"
        f"Type      : {feedback_type}\n"
        f"---\n"
        f"{description.strip()}\n\n"
    )

    with open(file_log, "a", encoding="utf-8") as file:
        file.write(log_entry)
    
    send_report(title, description, file_log)
    print(f"Feedback written to {file_log}")
              
def send_report(title, description, file_log):
    GITHUB_TOKEN = key.load_git_token()
    REPO_NAME = "lex890/cryptocurrency-investment-risk-assessment-tool"
    ISSUE_TITLE = title
    ISSUE_DESCRIPTION = description
    LOG_FILE_PATH = file_log or None

    create_github_issue(REPO_NAME, GITHUB_TOKEN, ISSUE_TITLE, ISSUE_DESCRIPTION, LOG_FILE_PATH)

def create_github_issue(repo_name, token, title, description, log_file_path):
    try:
        # Authenticate with GitHub
        g = Github(token)
        
        # Get the repository
        repo = g.get_repo(repo_name)
        
        # Initialize full description
        full_description = description
        
        # Process log file only if provided
        if log_file_path and isinstance(log_file_path, str) and log_file_path.strip():
            if not os.path.exists(log_file_path):
                raise FileNotFoundError(f"Log file {log_file_path} not found")
            
            with open(log_file_path, 'r', encoding='utf-8') as file:
                log_content = file.read()
            
            # Create a Gist for the log file using the authenticated user
            user = g.get_user()
            gist = user.create_gist(
                public=False,
                files={os.path.basename(log_file_path): github.InputFileContent(content=log_content)},
                description=f"Log file for issue: {title}"
            )
            
            # Append Gist URL to the issue description
            full_description = f"{description}\n\nAttached log file: {gist.html_url}"
        
        # Create the issue
        issue = repo.create_issue(
            title=title,
            body=full_description
        )
        
        print(f"Issue created successfully: {issue.html_url}")
    
    except FileNotFoundError as fnf:
        print(f"File error: {str(fnf)}")
        return None
    except github.GithubException as ghe:
        if ghe.status == 404:
            print("Error: Repository not found or you lack access. Check the repository name (e.g., 'owner/repo') and token permissions.")
        elif ghe.status == 401:
            print("Error: Invalid or expired GitHub token. Verify your token has 'repo' and 'gist' scopes.")
        else:
            print(f"GitHub API error: {ghe.status} - {ghe.message}")
        return None
    except Exception as e:
        print(f"Error creating issue: {str(e)}")
        send_automated_report()
        return None

def send_automated_report():
    error_trace = traceback.format_exc()
    current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    feedback_type = 'Other'
    description = f'Error:\n{error_trace}'
    sg.popup_error(description)
    submit_report(current_date, description, feedback_type, description, 'main.exe', 'automated report')