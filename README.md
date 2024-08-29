<!-- PROJECT LOGO -->
<p align="center" width="100%">
    <img src="static/logo_header.svg">
</p>


  <p align="center">
     <span style="font-size: 24px;">An Open-Source Data Platform</span>
    <br />
    <br />
     <span style="font-size: 16px;">Metrics, Models, Jobs, Pages, End-to-end column lineage, and more!</span>
    <br />
    <span style="font-size: 16px;">Define your source of truth with an open standard.</span>
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
## Data toolset as good as software tools
*Placeholder: add demo here*

**The problem:** Today's data stack is highly fragmented, insecure, and overpriced.
- Most teams we've talked to have at least 5-10 tools in their data stack. They often don't work well together.
- Today's closed ecosystem is vulnerable to [security breaches](https://www.wired.com/story/snowflake-breach-advanced-auto-parts-lendingtree/) and [tool discontinuation](https://news.ycombinator.com/item?id=40750391).
- Vendor lock-in has led to [exorbitant costs](https://aws.amazon.com/marketplace/pp/prodview-tjpcf42nbnhko) and [rent-seeking behavior](https://www.fool.com/investing/2022/08/26/3-wild-metrics-highlight-snowflakes-staggering-mom/):


**The Solution:** Turntable, a post-modern data stack
- *Open:* Our whole repo is AGPL and always will be. 
- *Private:* Self-deploy our open-source version or use our cloud product with our customer-deployed agent. Either way, your data never leaves your infrastructure.
- *Integrated:* With Turntable, all of your metrics, models, and data documents exist in the same context. We think this will allow for some totally new experiences. Think clicking on a dashboard and seeing exactly where a number came from.

## ✨ Features
- [x] **End-to-end Column lineage**: See your data's journey from source to dashboard.
- [x] **Documentation**: See all your data assets in one place. We event write AI-generated descriptions for you (opt-in of course).
- [x] **Pages**: Write and schedule analyses, reports, and data documents in a Notion-like interface.
- [x] **Jobs**: Schedule and monitor your data pipelines.
- [ ] **Full observability suite**: Detect anomalies, monitor data quality, reduce cost, secure PII and more.
- [ ] **Metrics:** Define once, use anywhere, in pure SQL and GUI. No need to learn a new semantic layer framework. 
- [ ] **Subscriptions**: Subscribe to data assets and get notified when they change. Each user gets their own dashboard
- [ ] **Models:** Allow team members to schedule and publish sql queries that depend on one another, with best practices already built in. 
- [ ] **CLI**: Use the code editor you already love, but make secure onboarding a breeze.


## 🔔 Stay up to date
Turntable launched its v0.1 on August 2024. Lots of new features are coming, and are generally released on a bi-weekly basis. Watch updates of this repository to be notified of future updates.

[Check out our public roadmap](https://turntable-so.canny.io/)

## 🙏 Credits

Our repo stands on the shoulders of some awesome open source projects. A big reason we decided to go open source is that there are lots of players in the data space who wrap open source projects in a proprietary layer and charge a lot for it. That didn't feel right to us.

With that context, we wanted to explicitly call out some of the projects we love and how we use them:

- [Ag-Grid](https://github.com/ag-grid/ag-grid): Table component
- [DataHub](https://github.com/datahub-project/datahub): metadata ingest engine
- [Django](https://github.com/django/django): Core application framework
- [Hatchet](https://github.com/hatchet-dev/hatchet):*workflow scheduler
- [Ibis](https://github.com/ibis-project/ibis): metrics layer and database connectors
- [Instructor](https://github.com/jxnl/instructor): structured AI output
- [Lago](https://github.com/getlago/lago): inspiration for our documentation
- [Mintlify](https://github.com/mintlify): docs site generator
- [Nivo](https://github.com/plouc/nivo): charting
- [Posthog](https://github.com/posthog/posthog): analytics
- [Reactflow](https://github.com/xyflow/xyflow): lineage canvas
- [Recharts](https://github.com/recharts/recharts): charting
- [Rye](https://github.com/astral-sh/rye): package management
- [SQLGlot](https://github.com/tobymao/sqlglot): sql/lineage parser
- [TipTap](https://github.com/ueberdosis/tiptap): Text editor

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
Create a `.env` file in the root of the project by running the following command

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

a. No demo resources

Run the following command:

```bash
docker compose --env-file .env up --build
```

Once the docker build is complete (a few minutes), you will see a line in the terminal like this: 'The app is ready! Visit http://localhost:3000/ to get started'. Once you do, open your browser and go to http://localhost:3000 to see the app running. Signup with a username and password to start using the app.

b. Demo resources

If you'd like to also see the product with a demo postgres dbt project and metabase already connected, run:

```bash
docker compose --env-file .env -f docker-compose.demo.yml up --build
```

Once the docker build is complete (longer than above, usually 5+ minutes), you will see a line in the terminal like this: 'The app is ready! Visit http://localhost:3000/ to get started'. Once you do, open your browser and go to http://localhost:3000 to see the app running. The demo resources can be found in an account with user `dev@turntable.so` and password `mypassword`. Login with these credentials to see the demo resources, with associated lineage and asset viewer. If you'd like to start from a blank slate on this instance, simply sign up with a different email.

### Analytics and tracking for the self-hosted version
Please note that Turntable, by default, tracks basic actions performed on your self-hosted instance, but you can easily opt out by setting the value of `NEXT_PUBLIC_POSTHOG_KEY` to `""` in the docker-compose yml file you are using (e.g. `docker-compose.yml` or `docker-compose.demo.yml`). We do not track any telemetry in development (i.e. using `docker-compose.dev.yml`).

For more information, please see our [privacy policy](www.turntable.so/privacy).

## ☁️ Use our cloud-based product
[Email us](mailto:founders@turntable.so) or visit [our website](www.turntable.so) to get started with our cloud product. There our two vairants: a fully-hosted offering, and hybrid one, which includes a customer-deployed agent. The agent allows you to keep all sensitive data and credentials on-premise.

## 🚀 Getting the most out of Turntable
- See the [documentation](https://doc.turntable.so) to learn more about all the features;
- Join our [Slack community](https://join.slack.com/t/turntable-community/shared_invite/zt-25p0olvhz-Z~c5QWq1jv2YFHQ46mMFDA) if you need help, or want to chat, we’re here to help;
- Follow us on [Twitter](https://twitter.com/Turntable) or [LinkedIn](https://www.linkedin.com/company/turntabledata) for the latest news;
- You can email us as well: [team@turnable.so](mailto:team@turntable.so).

## 📝 Contributing

You can follow the instructions below to set up ourm development environment on your machine. This is intended for people interested in contributing to Turntable. If you just want to try Turntable on your local system, we recommend that you the instructions above to run a prod instance.

For now, we are not accepting pull requests from the community, but We are working on a process to make this possible in the future. For now, file an bug reports and feature requests as a [GitHub issue](https://github.com/turntable-so/turntable/issues), [Canny submission](https://turntable-so.canny.io/) or [Slack post](https://join.slack.com/t/turntable-community/shared_invite/zt-25p0olvhz-Z~c5QWq1jv2YFHQ46mMFDA).

## 🧑‍💻 Development environment

To start the development environment, simply follow the instructions above to start the app, but change the final commmand to:

```bash
docker compose -f docker-compose.dev.yml --env-file .env up --build
```

Unlike the production environemnt, this supports hot reload. It also includes the demo resources described above.

Once everything starts (several minutes), run the command below to access a shell inside the container:

```bash
docker compose exec worker bash
```

From here, backend tests can be run with `pytest`.


