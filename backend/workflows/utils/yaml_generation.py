import yaml
import time
import uuid

def metabase_yaml_generation_path(url, environment, username, password):
  CONFIG = """
  source:
    type: metabase
    config:
      connect_uri: '{url}'
      username: '{username}'
      password: '{password}'
      env: '{environment}'
  sink:
    type: datahub-lite
  """
  # generate random name for .yaml file
  timestamp = int(time.time())  # Get the current timestamp
  unique_id = uuid.uuid4().hex  # Generate a unique identifier
  filename = f"temp_{timestamp}_{unique_id}.yaml"

  with open(filename, "w") as f:
    f.write(CONFIG.format(url=url, environment=environment, username=username, password=password))
  return filename

def tableau_yaml_generation_path(url, environment, username, password):
  CONFIG = """
  source:
    type: tableau
    config:
      connect_uri: '{url}'
      username: '{username}'
      password: '{password}'
      env: '{environment}'
  sink:
    type: datahub-lite
  """
  # generate random name for .yaml file
  timestamp = int(time.time())  # Get the current timestamp
  unique_id = uuid.uuid4().hex  # Generate a unique identifier
  filename = f"temp_{timestamp}_{unique_id}.yaml"

  with open(filename, "w") as f:
    f.write(CONFIG.format(url=url, environment=environment, username=username, password=password))
  return filename

def looker_yaml_generation_path(url, username, password):
  CONFIG = """
  source:
    type: looker
    config:
      base_url: '{url}'
      client_id: '{client_id}'
      client_secret: '{client_secret}'
  sink:
    type: datahub-lite
  """
  # generate random name for .yaml file
  timestamp = int(time.time())  # Get the current timestamp
  unique_id = uuid.uuid4().hex  # Generate a unique identifier
  filename = f"temp_{timestamp}_{unique_id}.yaml"

  with open(filename, "w") as f:
    f.write(CONFIG.format(url=url, client_id=username, client_secret=password))
  return filename