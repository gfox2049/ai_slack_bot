import pandas as pd 
import string
import json
import csv
import boto3
import urllib3
import os
from io import StringIO 
from botocore.response import StreamingBody
from atlassian import Jira



def comp_func(s1,s2):

    if len(s1) > len(s2):

        temp_s2 = s1
        temp_s1 = s2

        s1 = temp_s1
        s2 = temp_s2

    s1 = s1.lower()

    s2 = s2.lower()
    
    w_score = 0

    #s1 = s1.translate(str.maketrans('', '', string.punctuation))
    
    #s1 = ''.join(' ' if c in string.punctuation else c for c in s1)
    
    s1_list = s1.split()

    for s1w in s1_list:
        
        # semi-tokenization - word prefix
        if s1w in s2:
        
            score = len(s1w)
            
        #elif s1w[0:3] in s2:
            
        #    score = 3
            
        else:
            
            score = 0

        w_score = w_score + score
    
    return w_score


bedrock = boto3.client(service_name='bedrock-runtime')
agent = boto3.client(service_name='bedrock-agent-runtime')

slackUrl = 'https://company.slack.com/api/'
slackToken = os.environ.get('token')

http = urllib3.PoolManager()

sc = os.environ['sc']

jira = Jira(
    url='https://company.atlassian.net',
    username='john.l@company.com',
    password=sc)

def call_bedrock(question):
    
    question = question.replace('slackmode','')
    question = question.replace('wikimode','')
    question = question.replace('yodamode','')
    question = question.replace('gitmode','')
    question = question.replace('solarmode','')
    question = question.replace('jiramode','')
    question = question.replace('sqlmode','')
    question = question.replace('recruit3r','')
    question = question.replace('qa_helper','')
    
    # claude body
    #body = json.dumps({
    #    "prompt": f"\n\nHuman:  {question} \n\nAssistant:",
    #    "max_tokens_to_sample": 5000,
    #})
    
    system_prompt = '''You are Claude, an AI assistant used by company to be helpful,
                harmless, and honest. Your goal is to provide informative and substantive responses
                to queries while avoiding potential harms.'''
    
    # claude3 body
    body=json.dumps(
        {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 1000,
            "system": system_prompt,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": f"\n\nHuman:  {question} \n\nAssistant:"
                        }
                    ]
                }
            ]
        } 
    ) 
    
    ## titan body
    #body = json.dumps({
    #    "inputText": question,
    #    "textGenerationConfig": {
    #        "maxTokenCount": 4096,
    #        "stopSequences": [],
    #        "temperature": 0,
    #        "topP": .9
    #    }
    #})
    
    ## llama body
    #body = json.dumps({
    #    "prompt": question,
    #    "max_gen_len": 1000,
    #    "temperature": .1,
    #    "top_p": .9
    #})
    

    #modelId = 'anthropic.claude-v2:1'
    modelId = 'anthropic.claude-3-sonnet-20240229-v1:0'
    #modelId = 'amazon.titan-text-express-v1'
    #modelId = 'meta.llama2-70b-chat-v1'
    accept = 'application/json'
    contentType = 'application/json'
    
    print('invoke_model')
    
        
    response = bedrock.invoke_model(body=body, modelId=modelId, accept=accept, contentType=contentType)

    response_body = json.loads(response.get('body').read())
    
    print(str(response_body))

    #claude
    #fin_res = response_body.get("completion")
    
    #claude3
    fin_res = response_body['content'][0]['text']
    
    #titan
    #fin_res = ''
    #for result in response_body['results']:
    #    fin_res = fin_res + result['outputText']
    
    #llama
    #fin_res = response_body['generation']
    
    fin_res = fin_res.replace('\@qabot','[qabot]')
    fin_res = fin_res.replace('slackmode','')
    fin_res = fin_res.replace('wikimode','')
    fin_res = fin_res.replace('yodamode','')
    fin_res = fin_res.replace('sqlmode','')
    fin_res = fin_res.replace('gitmode','')
    fin_res = fin_res.replace('solarmode','')
    fin_res = fin_res.replace('jiramode','')
    fin_res = fin_res.replace('recruit3r','')
    fin_res = fin_res.replace('qa_helper','')
        
    
    return fin_res 
    


def invoke_agent(prompt):


    response = agent.invoke_agent(
        agentId='',
        agentAliasId='',
        sessionId='r2d2mode',
        inputText=prompt
    )

    completion = ""

    for event in response.get("completion"):
        chunk = event["chunk"]
        completion = completion + chunk["bytes"].decode()


    return completion


#def lambda_handler(event, context):
#    for record in event['Records']:
#        process_message(record)
#    print("done")
    

#def process_message(record):
#    try:
#        message = record['Sns']['Message']
#        print(f"Processed message {message}")
#        # TODO; Process your record here
    
 
def lambda_handler(event, context):

    run = False
    
    #print(f"Received event:\n{event}\nWith context:\n{context}")
    
    slackBody = json.loads(event['body'])
    print(str(slackBody))
    slackText = slackBody.get('event').get('text')
    slackUser = slackBody.get('event').get('user')
    channel =  slackBody.get('event').get('channel')
    challenge = slackBody.get('event').get('challenge')
    

    # check for message already processed
    
    msg_txt = channel + '-' + slackText + '-' + slackUser

    pdf = pd.DataFrame([msg_txt], columns=[0])
    
    key = 'qry_hist.csv'
    bucket = 'bedrock1kb1'
    s3_resource = boto3.resource('s3')
    s3_object = s3_resource.Object(bucket, key)
    
    try:
        
        data = s3_object.get()['Body'].read().decode('utf-8').splitlines()
    
        pdat = pd.DataFrame(data)
    
    except:
        
        data = pd.DataFrame(['none'], columns=[0])
        
    pdatz = pdat.tail(10)
    
    histall = pdatz[0].str.cat(sep=', ')
    
    if msg_txt in histall:
    
        print('query allready processed, ignoring')
    
    else:
    
        print('new query, processing')
    
        pdatx = pd.concat([pdatz,pdf], ignore_index=True)
    
        bucket = 'bedrock1kb1' # already created on S3
        csv_buffer = StringIO()
        pdatx.to_csv(csv_buffer)
        s3_resource = boto3.resource('s3')
        s3_resource.Object(bucket, 'qry_hist.csv').put(Body=csv_buffer.getvalue())


        headers = {
            'Authorization': f'Bearer {slackToken}',
            'Content-Type': 'application/json',
        }   
                    
    
        if 'slackmode' in slackText:
    
            slackText = slackText.replace('slackmode','')
               
            #reshist = http.request('GET', slackUrl  + 'conversations.list', headers=headers)
        
            #jl = json.loads(reshist.data)['channels']
            #cid = [x for x in jl if x['name'] == channel][0]['id']
                
            
            hist = {
                'channel': channel,
                'limit' : 40
            }
            
            reshist = http.request('POST', slackUrl  + 'conversations.history', headers=headers, body=json.dumps(hist))
            
            print( 'data size = ' + str(len(str(reshist.data))) + ' ' + str(reshist.data)[0:1000] )
        
            stres = str(json.loads(reshist.data)['messages'])
            
            stres = '\n\nSlack Channel Message History Text Context:\n\n' + stres +'\n\nThe text field is the message content - the most important.\n\nQuestion:\n\n' + slackText
            
            run = True
            
            
            
        elif 'jiramode' in slackText:

            slackText = slackText.replace('jiramode','')
            
            board_id = 93 # ENG
               
            jqlres = '''(resolutiondate >= startOfWeek() AND resolution = Done)'''
        
            jout = jira.get_issues_for_board(board_id, jql=jqlres, 
                                             fields="key,name,summary,resolutiondate,resolved", start=0, limit=None, expand=None)
            
            
            pout = pd.json_normalize(jout['issues'])
            
            
            
            pdf = pd.DataFrame(columns=['labels','description'])
            for i in pout['id']:
            
                jf = jira.issue(key=i)['fields']
            
                jpd = pd.json_normalize(jf)[['labels','description']]
            
                jpd['key'] = i
                
                pdf = pd.concat([jpd,pdf], ignore_index=True)
            
            pdfin = pd.merge(pdf, pout, left_on='key', right_on='id', how='inner')
            
            jz = json.dumps(pdfin.to_json())
            
    
            
            stres = '\n\nJira Context:\n\n' + str(jz) +'\n\nQuestion:\n\n' + slackText
            
            run = True



        elif 'solarmode' in slackText:
            
            slackText = slackText.replace('solarmode','')
            
            #key = 'dpd_all.csv'. # file w/ text splits
            key = 'gitdocs-2.csv' # file w/o text splits
            bucket = 'bedrock1kb1'
            s3_resource = boto3.resource('s3')
            s3_object = s3_resource.Object(bucket, key)
            
            data = s3_object.get()['Body'].read().decode('utf-8').splitlines()
            pdat = pd.DataFrame(data)
            
            pdat['dist'] = pdat.apply(lambda x: comp_func(slackText,x[0]), axis=1)
            
            pdat = pdat.sort_values(['dist'],ascending=False, ignore_index=True).head(1)
            
            stres = pdat[0].str.cat(sep=', ')
            
            stres = '\n\nAnswer based on the Context if sure of a truthful answer.  Solution Architect GitHub Context:\n\n' + stres +'\n\nQuestion:\n\n' + slackText
            
            run = True
            
            
            
        elif 'wikimode' in slackText:
            
            slackText = slackText.replace('wikimode','')
            
            key = 'all_docz-2.csv'
            bucket = 'bedrock1kb1'
            s3_resource = boto3.resource('s3')
            s3_object = s3_resource.Object(bucket, key)
            
            data = s3_object.get()['Body'].read().decode('utf-8').splitlines()
            pdat = pd.DataFrame(data)
            
            pdat['dist'] = pdat.apply(lambda x: comp_func(slackText,x[0]), axis=1)
            
            pdat = pdat.sort_values(['dist'],ascending=False, ignore_index=True).head(4)
            
            stres = pdat[0].str.cat(sep=', ')
            
            stres = '\n\nConfluence Wiki Text Context:\n\n' + stres +'\n\nThe text field is the most important.\n\nQuestion:\n\n' + slackText
            
            run = True
            


        elif 'sqlmode' in slackText:
            
            slackText = slackText.replace('sqlmode','')
            
            #if 'analytics' in slackText:
            #
            #    key = 'atic.csv'
            #    bucket = 'bedrock1kb1'
            #    s3_resource = boto3.resource('s3')
            #    s3_object = s3_resource.Object(bucket, key)
                
            #else:
                
            key = 'primo2.csv'
            bucket = 'bedrock1kb1'
            s3_resource = boto3.resource('s3')
            s3_object = s3_resource.Object(bucket, key)
            
            data = s3_object.get()['Body'].read().decode('utf-8').splitlines()
            
            # read entire file into dataframe becomes context
            
            stres = pd.DataFrame(data)
            
            stres = stres[0].str.cat(sep=', ')
            
            #stres = stres[0:100000]
            
            stres = 'Athena SQL DDL Context: ' + \
            '''This data is from the exported table DDL from Athena databases used by company solution architects.
            The first line contains table and column headers that explain the meaning of the columns.
            Do not infer textual values of data in columns for any filters.  Do not make up table names that do not exit in the context.''' + stres + \
            'Question from user: ' + slackText
            
            
            
            run = True
            
 
        elif 'recruit3r' in slackText:
            
            slackText = slackText.replace('recruit3r','')

            key = 'jdesc.txt'
            bucket = 'bedrock1kb1'
            s3_resource = boto3.resource('s3')
            s3_object = s3_resource.Object(bucket, key)
            
            jdesc = s3_object.get()['Body'].read().decode('utf-8')
            
            jdesc = '''Job description:
            ''' + jdesc
            
            key = 'res_out.txt'
            bucket = 'bedrock1kb1'
            s3_resource = boto3.resource('s3')
            s3_object = s3_resource.Object(bucket, key)
            
            res_out = s3_object.get()['Body'].read().decode('utf-8')
            
            res_out = '''Candidate resumes:
            ''' + res_out
            
            stres = jdesc + res_out
            
            stres = 'Recruiting Agent Helper Context: ' + \
            '''The following context contains a job description for a role that is currently being sourced,
            as well as candidate resumes to be considered for that position.''' + stres + \
            'Question from user: ' + slackText
            
            
            run = True
            

        elif 'qa_helper' in slackText:
            
            slackText = slackText.replace('qa_helper','')

            '''
            hist = {
                'channel': channel,
                'limit' : 6
            }
            
            reshist = http.request('POST', slackUrl  + 'conversations.history', headers=headers, body=json.dumps(hist))
            
            print( 'data size = ' + str(len(str(reshist.data))) + ' ' + str(reshist.data)[0:1000] )
        
            stres = str(json.loads(reshist.data)['messages'])
            
            #stres = Your role is to ask up to 6 questions of the candidate you have been introduced to in the channel.
            #The candidate's name will match a name in the resumes context.  
            #Questions should be appropriate to better screen the candidate based on the job description and their experience from their resume.
            #First greet the candidate in a friendly manner, then present up to 6 questions to ask them as mentioned above.
            #Slack channel history context:
            #Remember to not repeat any question that has already been asked unless the user asks for clarification.
            + stres
            
            '''
            
    
            key = 'jdesc.txt'
            bucket = 'bedrock1kb1'
            s3_resource = boto3.resource('s3')
            s3_object = s3_resource.Object(bucket, key)
            
            jdesc = s3_object.get()['Body'].read().decode('utf-8')
            
            jdesc = '''Job description:
            ''' + jdesc
            
            key = 'res_out.txt'
            bucket = 'bedrock1kb1'
            s3_resource = boto3.resource('s3')
            s3_object = s3_resource.Object(bucket, key)
            
            res_out = s3_object.get()['Body'].read().decode('utf-8')
            
            res_out = '''Candidate resumes:
            ''' + res_out
            
            stres = jdesc + res_out
            
            stres = 'Recruiting Agent Helper Context: ' + \
            '''The following context contains a job description for a role that is currently being sourced,
            as well as candidate resumes to be considered for that position.''' + stres + \
            'List 6 questions to ask the candidate introduced here: ' + slackText
            
            
            run = True
            
            
        
        elif 'gitmode' in slackText:
            
            slackText = slackText.replace('gitmode','')
            
            key = 'dpd_all.csv'
            bucket = 'bedrock1kb1'
            s3_resource = boto3.resource('s3')
            s3_object = s3_resource.Object(bucket, key)
            
            data = s3_object.get()['Body'].read().decode('utf-8').splitlines()
            pdat = pd.DataFrame(data)
            
            pdat['dist'] = pdat.apply(lambda x: comp_func(slackText,x[0]), axis=1)
            
            pdat = pdat.sort_values(['dist'],ascending=False, ignore_index=True).head(4)
            
            stres = pdat[0].str.cat(sep=', ')
            
            stres = '\n\nGit Repo Context:\n\n' + stres +'\n\nQuestion:\n\n' + slackText
            
            run = True
    
        
        
        elif 'yodamode' in slackText:
            
            slackText = slackText.replace('yodamode','')
            
            stres = slackText
            
            run = True
            
        
        else:
            
            msg = 'Please provide a tag for the bot.  Thank you.'
        
            #msg = 'Please use a tag for the bot - slackmode for channel history, wikimode for confluence, jiramode for closed issues, or yodamode for global LLM'
        
            data = {'channel': channel, 'text': f"<@{slackUser}> {msg}"}
        
            response = http.request('POST', slackUrl  + 'chat.postMessage', headers=headers, body=json.dumps(data))
            
            
            
        if run == True:  
            
            sres = 'Human:  Answer the question if you are sure of a truthful answer.\n\n' + stres + '\n\nAssistant:\n\n'
                
            print('calling bedrock function')
            
            msg = call_bedrock(stres)
        
            data = {'channel': channel, 'text': f"<@{slackUser}> {msg}"}
        
            response = http.request('POST', slackUrl  + 'chat.postMessage', headers=headers, body=json.dumps(data))
            
            
            
        #return response.data
        
        return {
            'statusCode': 200,
            'body': json.dumps(slackBody)
        }
