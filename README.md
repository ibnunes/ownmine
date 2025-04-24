# ownmine 2.0

**Simple automation toolkit for self-hosted Minecraft servers**

🚧 **Version 2 is in development!**

I'm migrating the collection of Bash scripts to a minimalist local client/server tool written in **Python 3.11+**. This will finally allow support for **multiple Minecraft server instances**, background execution, and improved flexibility.

If you're checking out this branch, stay tuned 😉


## Roadmap

### Core

- [x] Replace Bash scripts with Python
- [x] Daemon that listens on a UNIX socket
- [x] Minimalist CLI client
- [x] Build a JSON-based configuration system
- [x] Secure config storage (encrypted passwords)
- [ ] Manage servers via CLI
- [ ] Push and pull backups
- [ ] Push backups to SMB shares
- [ ] Tests & validation


### Extras

- [ ] Improve logging and error handling
- [ ] Allow jar options configuration
- [ ] Add status and health checks
- [ ] Allow key regen


### Future

- [ ] Schedule backups
- [ ] Configure scheduled actions
- [ ] Automate key regen
