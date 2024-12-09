<!-- PROJECT LOGO -->
<p align="center" width="100%">
    <img src="static/logo_header.svg">
</p>

  <p align="center">
     <span style="font-size: 24px;">The open source IDE for data teams that use dbt</span>
    <br />
    <br />
     <span style="font-size: 16px;">Asset catalog, end-to-end column-level lineage, isolated environments & workspaces, code IDE, AI assistant and more!</span>
    <br />
    <br />
    <a href="https://join.slack.com/t/turntable-community/shared_invite/zt-25p0olvhz-Z~c5QWq1jv2YFHQ46mMFDA">Slack</a>
    ·
    <a href="https://www.turntable.so">Website</a>
    ·
    <a href="https://github.com/turntable-so/turntable/issues">Issues</a>
    ·
    <a href="https://turntable.productlane.com/roadmap">Roadmap</a>
  </p>

<p align="center">
   <a href="https://join.slack.com/t/turntable-community/shared_invite/zt-25p0olvhz-Z~c5QWq1jv2YFHQ46mMFDA"><img src="https://img.shields.io/badge/Turntable%20Slack%20Community-turntable.slack.com-%234A154B" alt="Join Turntable on Slack"></a>
   <a href="https://github.com/turntable-so/turntable/stargazers"><img src="https://img.shields.io/github/stars/turntable-so/turntable" alt="Github Stars"></a>
   <!-- <a href="https://news.ycombinator.com/item?id=31424450"><img src="https://img.shields.io/badge/Hacker%20News-777-%23FF6600" alt="Hacker News"></a> -->
   <a href="https://github.com/turntable-so/blob/main/LICENSE"><img src="https://img.shields.io/badge/license-AGPLv3-blue" alt="License"></a>
   <a href="https://www.ycombinator.com/companies/turntable"><img src="https://img.shields.io/badge/Backed%20by-Y%20Combinator-%23f26625"></a>
</p>

<!-- ABOUT THE PROJECT -->

## Open Source Web IDE for Data Teams that use dbt Core

<video src="https://github.com/user-attachments/assets/d0bb1be5-6b6c-4ab1-b949-ce5ec4c18c5e.mp4" width="320" height="240" controls autoplay></video>

**The problem:** Today's data stack is highly fragmented and expensive

- Most modern data teams have at least 5-10 tools in their data stack. They often don't work well together.
- Vendor lock-in has led to [exorbitant costs](https://aws.amazon.com/marketplace/pp/prodview-tjpcf42nbnhko) and [rent-seeking behavior](https://www.fool.com/investing/2022/08/26/3-wild-metrics-highlight-snowflakes-staggering-mom/):

**The Solution:** Turntable, a post-modern data stack

- _Open:_ Our whole repo is AGPL and always will be.
- _Private:_ Self-deploy our open-source version or use our cloud product with our customer-deployed agent. Either way, your data never leaves your infrastructure.
- _Integrated:_ With Turntable, all of your metrics, models, and data documents exist in the same context. We think this will allow for some totally new experiences. Think clicking on a dashboard and seeing exactly where a number came from.

## ✨ Features

- [x] **End-to-end Column lineage**: See your data's journey from source to dashboard.
- [x] **Code IDE**: Develop, test, and deploy your dbt projects in an easy to use web IDE.
- [x] **AI assistant**: Spend less time writing dbt models, documentation and tests with a full integrated AI assistant.
- [x] **Data catalog**: See all your data assets in one place. We event write AI-generated descriptions for you (opt-in of course).
- [x] **Jobs**: Schedule and monitor your data pipelines.
- [x] **BI tool integration**: Ingest charts and dashboards from BI tools and discover usage patterns, unused assets and identify breaking changes.
- [ ] **Agentic workflows (coming soon)**: Longer-running AI workflows to build multiple dbt models and dashboards, deprecate unused assets and optimize your pipelines.
- [ ] **Full observability suite (coming soon)**: Detect anomalies, monitor data quality, reduce cost, secure PII and more.
- [ ] **Metrics:** Define once, use anywhere, in pure SQL and GUI. No need to learn a new semantic layer framework.
- [ ] **Subscriptions**: Subscribe to data assets and get notified when they change. Each user gets their own dashboard

## 🔌 Integrations

**Data Sources**: Postgres, Snowflake, BigQuery, DuckDB, Redshift, S3, and more.

**BI Tools**: Looker, Tableau, Metabase, PowerBI.

**Data Transformation**: dbt Core, SqlMesh (coming soon)

**Saas Ingest (coming soon)**: Stripe, Zendesk, Hubspot, Salesforce, and more.

## 🔔 Stay up to date

Turntable launched its v0.1 on August 2024. Lots of new features are coming, and are generally released on a bi-weekly basis. Watch updates of this repository to be notified of future updates.

[Check out our public roadmap](https://turntable-so.canny.io/)

## 🔖 License

Turntable is distributed under the AGPLv3 License.

## 💻 Deploy locally

### Requirements

1. Install Docker on your machine;
2. Make sure Docker Compose is installed and available (it should be the case if you have chosen to install Docker via Docker Desktop); and
3. Make sure Git is installed on your machine.

### Run the app

To start using Turntable

1. Clone the repository

```bash
# Get the code
git clone https://github.com/turntable-so/turntable.git

# Go to Turntable folder
cd turntable
```

2. Configure environment variables
   Create a `.env.local` file in the root of the project by running the following command

**MacOS or Linux**

```bash
bash generate_keys.sh
```

**Windows**

```Powershell
powershell -executionpolicy bypass -File .\generate_keys.ps1
```

No environment variables except the secrets generated by the commands above are required to run the app, but some functionality may be limited (e.g. AI-written documentation). See `.env.example` for a list of all available environment variables.

3. Start the app

To start the app you have two choices:

**(A) Run Turntable with No demo resources**

Run the following command:

```bash
docker compose --env-file .env.local up --build
```

Once the docker build is complete (a few minutes), you will see a line in the terminal like this: 'The app is ready! Visit http://localhost:3000/ to get started'. Once you do, open your browser and go to http://localhost:3000 to see the app running. Signup with a username and password to start using the app.

**(B) Run Turntable with demo resources**

If you'd like to also see the product with a demo postgres, dbt project, and metabase already connected, run:

```bash
docker compose --env-file .env.local -f docker-compose.demo.yml up --build
```

Once the docker build is complete (longer than above, usually 5+ minutes), you will see a line in the terminal like this: 'The app is ready! Visit http://localhost:3000/ to get started'. Once you do, open your browser and go to http://localhost:3000 to see the app running. The demo resources can be found in an account with user `dev@turntable.so` and password `mypassword`. Login with these credentials to see the demo resources, with associated lineage and asset viewer. If you'd like to start from a blank slate on this instance, simply sign up with a different email.

### Analytics and tracking for the self-hosted version

Please note that Turntable, by default, tracks basic actions performed on your self-hosted instance, but you can easily opt out by setting the value of `NEXT_PUBLIC_POSTHOG_KEY` to `""` in the docker-compose yml file you are using (e.g. `docker-compose.yml` or `docker-compose.demo.yml`). We do not track any telemetry in development (i.e. using `docker-compose.dev.yml`).
For more information, please see our [privacy policy](www.turntable.so/privacy).

## ☁️ Use our cloud-based product

[Email us](mailto:team@turntable.so) or visit [our website](www.turntable.so) to get started with our cloud product. Their our two vairants: a fully-hosted offering, and hybrid one, which includes a customer-deployed agent.

## 🚀 Getting the most out of Turntable

- See the [documentation](https://doc.turntable.so) to learn more about all the features;
- Join our [Slack community](https://join.slack.com/t/turntable-community/shared_invite/zt-25p0olvhz-Z~c5QWq1jv2YFHQ46mMFDA) if you need help, or want to chat, we’re here to help;
- Follow us on [Twitter](https://twitter.com/Turntable) or [LinkedIn](https://www.linkedin.com/company/turntabledata) for the latest news;
- You can email us as well: [team@turnable.so](mailto:team@turntable.so).

## 📝 Contributing

You can follow the instructions below to set up ourm development environment on your machine. This is intended for people interested in contributing to Turntable. If you just want to try Turntable on your local system, we recommend that you the instructions above to run a prod instance.

For now, we are not accepting pull requests from the community, but We are working on a process to make this possible in the future. For now, file an bug reports and feature requests as a [GitHub issue](https://github.com/turntable-so/turntable/issues), [Roadmap submission](https://turntable.productlane.com/roadmap) or [Slack post](https://join.slack.com/t/turntable-community/shared_invite/zt-25p0olvhz-Z~c5QWq1jv2YFHQ46mMFDA).

## 🧑‍💻 Development environment

To start the development environment, simply follow the instructions above to start the app, but change the final commmand to:

```bash
docker compose -f docker-compose.dev.yml --env-file .env.local up --build
```

Unlike the production environemnt, this supports hot reload. It also includes the demo resources described above.

Once everything starts (several minutes), run the command below to access a shell inside the container:

```bash
docker compose -f docker-compose.dev.yml exec worker bash
```

From here, backend tests can be run with `pytest`.
