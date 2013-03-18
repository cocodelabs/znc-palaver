/*
 * ZNC Palaver Module
 *
 * Copyright (c) 2013 Kyle Fuller
 * License under the MIT license
 */

#define REQUIRESSL

#include <znc/Modules.h>
#include <znc/User.h>
#include <znc/IRCNetwork.h>
#include <znc/Client.h>
#include <znc/Chan.h>



const char *kPLVCapability = "palaverapp.com";
const char *kPLVCommand = "PALAVER";
const char *kPLVPushEndpointKey = "PUSH-ENDPOINT";
const char *kPLVMentionKeywordKey = "MENTION-KEYWORD";
const char *kPLVMentionChannelKey = "MENTION-CHANNEL";
const char *kPLVMentionNickKey = "MENTION-NICK";
const char *kPLVIgnoreKeywordKey = "IGNORE-KEYWORD";
const char *kPLVIgnoreChannelKey = "IGNORE-CHANNEL";
const char *kPLVIgnoreNickKey = "IGNORE-NICK";


class CDevice {
public:
	CDevice(const CString &sToken) {
		m_sToken = sToken;
		m_bInNegotiation = false;
	}

	CString GetVersion() const {
		return m_sVersion;
	}

	bool InNegotiation() const {
		return m_bInNegotiation;
	}

	void SetInNegotiation(bool inNegotiation) {
		m_bInNegotiation = inNegotiation;
	}

	void SetVersion(const CString &sVersion) {
		m_sVersion = sVersion;
	}

	CString GetToken() const {
		return m_sToken;
	}

	void SetPushEndpoint(const CString &sEndpoint) {
		m_sPushEndpoint = sEndpoint;
	}

	CString GetPushEndpoint() const {
		return m_sPushEndpoint;
	}

	bool HasClient(const CClient& client) const {
		bool bHasClient = false;

		for (std::vector<CClient*>::const_iterator it = m_vClients.begin();
				it != m_vClients.end(); ++it) {
			CClient *pCurrentClient = *it;

			if (&client == pCurrentClient) {
				bHasClient = true;
				break;
			}
		}

		return bHasClient;
	}

	void AddClient(CClient& client) {
		if (HasClient(client) == false) {
			m_vClients.push_back(&client);
		}
	}

	void RemoveClient(const CClient& client) {
		for (std::vector<CClient*>::iterator it = m_vClients.begin();
				it != m_vClients.end(); ++it) {
			CClient *pCurrentClient = *it;

			if (&client == pCurrentClient) {
				m_vClients.erase(it);
				break;
			}
		}
	}

	void AddNetwork(CIRCNetwork& network) {
		CUser *user = network.GetUser();
		const CString& sUsername = user->GetUserName();

		m_msvsNetworks[sUsername].push_back(network.GetName());
	}

	void RemoveNetwork(CIRCNetwork& network) {
		const CUser *user = network.GetUser();
		const CString& sUsername = user->GetUserName();

		std::map<CString, VCString>::iterator it = m_msvsNetworks.find(sUsername);
		if (it != m_msvsNetworks.end()) {
			VCString &networks = it->second;

			for (VCString::iterator it2 = networks.begin(); it2 != networks.end(); ++it2) {
				CString &name = *it2;

				if (name.Equals(network.GetName())) {
					networks.erase(it2);
					break;
				}
			}

			if (networks.empty()) {
				m_msvsNetworks.erase(it);
			}
		}
	}

	bool HasNetwork(CIRCNetwork& network) {
		bool hasNetwork = false;

		const CUser *user = network.GetUser();
		const CString& sUsername = user->GetUserName();

		std::map<CString, VCString>::iterator it = m_msvsNetworks.find(sUsername);
		if (it != m_msvsNetworks.end()) {
			VCString &networks = it->second;

			for (VCString::iterator it2 = networks.begin(); it2 != networks.end(); ++it2) {
				CString &name = *it2;

				if (name.Equals(network.GetName())) {
					hasNetwork = true;
					break;
				}
			}
		}

		return hasNetwork;
	}

	void ResetDevice() {
		m_bInNegotiation = false;
		m_sVersion = "";
		m_sPushEndpoint = "";

		m_vMentionKeywords.clear();
		m_vMentionChannels.clear();
		m_vMentionNicks.clear();
		m_vIgnoreKeywords.clear();
		m_vIgnoreChannels.clear();
		m_vIgnoreNicks.clear();
	}

	void AddMentionKeyword(const CString& sKeyword) {
		m_vMentionKeywords.push_back(sKeyword);
	}

	void AddMentionChannel(const CString& sChannel) {
		m_vMentionChannels.push_back(sChannel);
	}

	void AddMentionNick(const CString& sNick) {
		m_vMentionNicks.push_back(sNick);
	}

	void AddIgnoreKeyword(const CString& sKeyword) {
		m_vIgnoreKeywords.push_back(sKeyword);
	}

	void AddIgnoreChannel(const CString& sChannel) {
		m_vIgnoreChannels.push_back(sChannel);
	}

	void AddIgnoreNick(const CString& sNick) {
		m_vIgnoreNicks.push_back(sNick);
	}

	bool HasMentionChannel(const CString& sChannel) const {
		bool bResult = false;

		for (VCString::const_iterator it = m_vMentionChannels.begin();
				it != m_vMentionChannels.end(); ++it) {
			const CString& channel = *it;

			if (channel.WildCmp(sChannel)) {
				bResult = true;
				break;
			}
		}

		return bResult;
	}

	bool HasIgnoreChannel(const CString& sChannel) const {
		bool bResult = false;

		for (VCString::const_iterator it = m_vIgnoreChannels.begin();
				it != m_vIgnoreChannels.end(); ++it) {
			const CString& channel = *it;

			if (channel.WildCmp(sChannel)) {
				bResult = true;
				break;
			}
		}

		return bResult;
	}

	bool HasMentionNick(const CString& sNick) const {
		bool bResult = false;

		for (VCString::const_iterator it = m_vMentionNicks.begin();
				it != m_vMentionNicks.end(); ++it) {
			const CString& nick = *it;

			if (nick.WildCmp(sNick)) {
				bResult = true;
				break;
			}
		}

		return bResult;
	}

	bool HasIgnoreNick(const CString& sNick) const {
		bool bResult = false;

		for (VCString::const_iterator it = m_vIgnoreNicks.begin();
				it != m_vIgnoreNicks.end(); ++it) {
			const CString& nick = *it;

			if (nick.WildCmp(sNick)) {
				bResult = true;
				break;
			}
		}

		return bResult;
	}

	bool IncludesMentionKeyword(const CString& sMessage, const CString &sNick) const {
		bool bResult = false;

		for (VCString::const_iterator it = m_vMentionKeywords.begin();
				it != m_vMentionKeywords.end(); ++it) {
			const CString& sKeyword = *it;

			if (sKeyword.Equals("{nick}") && sMessage.find(sNick) != std::string::npos) {
				bResult = true;
				break;
			}

			if (sMessage.find(sKeyword) != std::string::npos) {
				bResult = true;
				break;
			}
		}

		return bResult;
	}

	bool IncludesIgnoreKeyword(const CString& sMessage) const {
		bool bResult = false;

		for (VCString::const_iterator it = m_vIgnoreKeywords.begin();
				it != m_vIgnoreKeywords.end(); ++it) {
			const CString& sKeyword = *it;

			if (sMessage.find(sKeyword) != std::string::npos) {
				bResult = true;
				break;
			}
		}

		return bResult;
	}

#pragma mark - Notifications

	void SendNotification(CModule& module, const CString& sSender, const CString& sNotification, const CChan *pChannel) {
		// todo parse from m_sPushEndpoint
		bool bUseTLS = true;
		CString sHostname = "api.palaverapp.com";
		unsigned short uPort = 443;
		CString sPath = "/1/push";

		CString sJSON = "{";
		sJSON += "\"message\": \"" + sNotification.Replace_n("\"", "\\\"") + "\"";
		sJSON += ",\"sender\": \"" + sSender.Replace_n("\"", "\\\"") + "\"";
		if (pChannel) {
			sJSON += ",\"channel\": \"" + pChannel->GetName().Replace_n("\"", "\\\"") + "\"";
		}
		sJSON += "}";

		CSocket *pSocket = new CSocket(&module);
		pSocket->Connect(sHostname, uPort, bUseTLS);
		pSocket->Write("POST " + sPath + " HTTP/1.1\r\n");
		pSocket->Write("Host: " + sHostname + "\r\n");
		pSocket->Write("Authorization: Bearer " + GetToken() + "\r\n");
		pSocket->Write("Connection: close\r\n");
		pSocket->Write("User-Agent: ZNC\r\n");
		pSocket->Write("Content-Type: application/json\r\n");
		pSocket->Write("Content-Length: " + CString(sJSON.length()) + "\r\n");
		pSocket->Write("\r\n");
		pSocket->Write(sJSON);
		pSocket->Close(Csock::CLT_AFTERWRITE);
		module.AddSocket(pSocket);
	}

	std::map<CString, VCString> GetNetworks() const {
		return m_msvsNetworks;
	}

private:
	CString m_sToken;
	CString m_sVersion;
	CString m_sPushEndpoint;

	std::map<CString, VCString> m_msvsNetworks;

	std::vector<CClient*> m_vClients;

	VCString m_vMentionKeywords;
	VCString m_vMentionChannels;
	VCString m_vMentionNicks;

	VCString m_vIgnoreKeywords;
	VCString m_vIgnoreChannels;
	VCString m_vIgnoreNicks;

	bool m_bInNegotiation;
};

class CPalaverMod : public CModule {
public:
	MODCONSTRUCTOR(CPalaverMod) {
		AddHelpCommand();
		AddCommand("test", static_cast<CModCommand::ModCmdFunc>(&CPalaverMod::HandleTestCommand),
			"", "Send notifications to registered devices");
		AddCommand("list", static_cast<CModCommand::ModCmdFunc>(&CPalaverMod::HandleListCommand),
			"", "List all registered devices");
	}

#pragma mark - Cap

	virtual void OnClientCapLs(CClient* pClient, SCString& ssCaps) {
		ssCaps.insert(kPLVCapability);
	}

	virtual bool IsClientCapSupported(CClient* pClient, const CString& sCap, bool bState) {
		return sCap.Equals(kPLVCapability);
	}

#pragma mark -

	virtual EModRet OnUserRaw(CString& sLine) {
		return HandleUserRaw(m_pClient, sLine);
	}

	virtual EModRet OnUnknownUserRaw(CClient* pClient, CString& sLine) {
		return HandleUserRaw(pClient, sLine);
	}

	virtual EModRet HandleUserRaw(CClient* pClient, CString& sLine) {
		if (sLine.Token(0).Equals(kPLVCommand)) {
			CString sCommand = sLine.Token(1);

			if (sCommand.Equals("BACKGROUND")) {
				m_pClient->SetAway(true);
			} else if (sCommand.Equals("FOREGROUND")) {
				m_pClient->SetAway(false);
			} else if (sCommand.Equals("IDENTIFY")) {
				CDevice *pDevice = DeviceForClient(*pClient);
				if (pDevice) {
					pDevice->RemoveClient(*pClient);
				}

				CString sToken = sLine.Token(2);
				CString sVersion = sLine.Token(3);

				CDevice& device = DeviceWithToken(sToken);

				if (device.InNegotiation() == false && device.GetVersion().Equals(sVersion) == false) {
					pClient->PutClient("PALAVER REQ *");
					device.SetInNegotiation(true);
				}

				device.AddClient(*pClient);

				if (m_pNetwork) {
					device.AddNetwork(*m_pNetwork);
				}
			} else if (sCommand.Equals("BEGIN")) {
				CString sToken = sLine.Token(2);
				CString sVersion = sLine.Token(3);
				CDevice& device = DeviceWithToken(sToken);

				device.ResetDevice();
				device.SetInNegotiation(true);
				device.SetVersion(sVersion);

				device.AddClient(*pClient);
			} else if (sCommand.Equals("END")) {
				CDevice *pDevice = DeviceForClient(*pClient);

				if (pDevice) {
					pDevice->SetInNegotiation(false);
				}
			} else if (sCommand.Equals("SET")) {
				CString sKey = sLine.Token(2);
				CString sValue = sLine.Token(3, true);

				CDevice *pDevice = DeviceForClient(*pClient);

				if (pDevice) {
					if (sKey.Equals("VERSION")) {
						pDevice->SetVersion(sValue);
					} else if (sKey.Equals(kPLVPushEndpointKey)) {
						pDevice->SetPushEndpoint(sValue);
					}
				}
			} else if (sCommand.Equals("ADD")) {
				CString sKey = sLine.Token(2);
				CString sValue = sLine.Token(3, true);

				CDevice *pDevice = DeviceForClient(*pClient);

				if (pDevice) {
					if (sKey.Equals(kPLVIgnoreKeywordKey)) {
						pDevice->AddIgnoreKeyword(sValue);
					} else if (sKey.Equals(kPLVIgnoreChannelKey)) {
						pDevice->AddIgnoreChannel(sValue);
					} else if (sKey.Equals(kPLVIgnoreNickKey)) {
						pDevice->AddIgnoreNick(sValue);
					} else if (sKey.Equals(kPLVMentionKeywordKey)) {
						pDevice->AddMentionKeyword(sValue);
					} else if (sKey.Equals(kPLVMentionChannelKey)) {
						pDevice->AddMentionChannel(sValue);
					} else if (sKey.Equals(kPLVMentionNickKey)) {
						pDevice->AddMentionNick(sValue);
					}
				}
			}

			return HALT;
		}

		return CONTINUE;
	}

#pragma mark -

	virtual void OnClientLogin() {
		// Associate client with the user/network
		CDevice *pDevice = DeviceForClient(*m_pClient);
		if (pDevice && m_pNetwork) {
			pDevice->AddNetwork(*m_pNetwork);
		}
	}

	virtual void OnClientDisconnect() {
		CDevice *pDevice = DeviceForClient(*m_pClient);
		if (pDevice) {
			pDevice->SetInNegotiation(false);
			pDevice->RemoveClient(*m_pClient);
		}
	}

#pragma mark -

	CDevice& DeviceWithToken(const CString& sToken) {
		CDevice *pDevice = NULL;

		for (std::vector<CDevice*>::const_iterator it = m_vDevices.begin();
				it != m_vDevices.end(); ++it) {
			CDevice& device = **it;

			if (device.GetToken().Equals(sToken)) {
				pDevice = &device;
				break;
			}
		}

		if (pDevice == NULL) {
			pDevice = new CDevice(sToken);
			m_vDevices.push_back(pDevice);
		}

		return *pDevice;
	}

	CDevice* DeviceForClient(CClient &client) const {
		CDevice *pDevice = NULL;

		for (std::vector<CDevice*>::const_iterator it = m_vDevices.begin();
				it != m_vDevices.end(); ++it) {
			CDevice& device = **it;

			if (device.HasClient(client)) {
				pDevice = &device;
				break;
			}
		}

		return pDevice;
	}

#pragma mark -

	void ParseMessage(CNick& Nick, CString& sMessage, CChan *pChannel = NULL) {
		if (m_pNetwork->IsUserOnline() == false) {
			for (std::vector<CDevice*>::const_iterator it = m_vDevices.begin();
					it != m_vDevices.end(); ++it)
			{
				CDevice& device = **it;

				if (device.HasNetwork(*m_pNetwork)) {
					bool bMention = (
						((pChannel == NULL) || device.HasMentionChannel(pChannel->GetName())) ||
						device.HasMentionNick(Nick.GetNick()) ||
						device.IncludesMentionKeyword(sMessage, m_pNetwork->GetIRCNick().GetNick()));

					if (bMention && (
							(pChannel && device.HasIgnoreChannel(pChannel->GetName())) ||
							device.HasIgnoreNick(Nick.GetNick()) ||
							device.IncludesIgnoreKeyword(sMessage)))
					{
						bMention = false;
					}

					if (bMention) {
						device.SendNotification(*this, Nick.GetNick(), sMessage, pChannel);
					}
				}
			}
		}
	}

	virtual EModRet OnChanMsg(CNick& Nick, CChan& Channel, CString& sMessage) {
		ParseMessage(Nick, sMessage, &Channel);
		return CONTINUE;
	}

	virtual EModRet OnPrivMsg(CNick& Nick, CString& sMessage) {
		ParseMessage(Nick, sMessage, NULL);
		return CONTINUE;
	}

#pragma mark - Commands

	void HandleTestCommand(const CString& sLine) {
		if (m_pNetwork) {
			unsigned int count = 0;

			for (std::vector<CDevice*>::const_iterator it = m_vDevices.begin();
					it != m_vDevices.end(); ++it)
			{
				CDevice& device = **it;

				if (device.HasNetwork(*m_pNetwork)) {
					count++;
					device.SendNotification(*this, "palaver", "Test notification", NULL);
				}
			}

			PutModule("Notification sent to " + CString(count) + " clients.");
		} else {
			PutModule("You need to connect with a network.");
		}
	}

	void HandleListCommand(const CString &sLine) {
		if (m_pUser->IsAdmin() == false) {
			PutModule("Permission denied");
			return;
		}

		CTable Table;

		Table.AddColumn("Device");
		Table.AddColumn("User");
		Table.AddColumn("Network");
		Table.AddColumn("Negotiating");

		for (std::vector<CDevice*>::const_iterator it = m_vDevices.begin();
				it != m_vDevices.end(); ++it)
		{
			CDevice &device = **it;

			const std::map<CString, VCString> msvsNetworks = device.GetNetworks();
			std::map<CString, VCString>::const_iterator it2 = msvsNetworks.begin();
			for (;it2 != msvsNetworks.end(); ++it2) {
				const CString sUsername = it2->first;
				const VCString &networks = it2->second;

				for (VCString::const_iterator it3 = networks.begin(); it3 != networks.end(); ++it3) {
					const CString sNetwork = *it3;

					Table.AddRow();
					Table.SetCell("Device", device.GetToken());
					Table.SetCell("User", sUsername);
					Table.SetCell("Network", sNetwork);
					Table.SetCell("Negotiating", CString(device.InNegotiation()));
				}

				if (networks.size() == 0) {
					Table.SetCell("Device", device.GetToken());
					Table.SetCell("User", sUsername);
					Table.SetCell("Network", "");
					Table.SetCell("Negotiating", CString(device.InNegotiation()));
				}
			}

			if (msvsNetworks.size() == 0) {
				Table.SetCell("Device", device.GetToken());
				Table.SetCell("User", "");
				Table.SetCell("Network", "");
				Table.SetCell("Negotiating", CString(device.InNegotiation()));
			}
		}

		if (PutModule(Table) == 0) {
			PutModule("There are no devices registered with this server.");
		}

		CDevice *pDevice = DeviceForClient(*m_pClient);
		if (pDevice) {
			PutModule("You are connected from Palaver. (" + pDevice->GetToken() + ")");
		} else {
			PutModule("You are not connected from a Palaver client.");
		}
	}

private:

	std::vector<CDevice*> m_vDevices;
};

GLOBALMODULEDEFS(CPalaverMod, "Palaver support module")

