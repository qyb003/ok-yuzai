/**
 * OKX Wallet Section - Testnet/Mainnet API key configuration  [OKX 新增]
 *
 * Full wallet configuration UI for OKX Perpetual Futures.
 * Uses API Key + Secret Key + Passphrase (OKX requires all three).
 */
import { useState, useEffect } from 'react'
import toast from 'react-hot-toast'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { Wallet, Eye, EyeOff, CheckCircle, RefreshCw, Trash2 } from 'lucide-react'
import { useTranslation } from 'react-i18next'

interface OkxWalletSectionProps {
  accountId: number
  accountName: string
  onStatusChange?: (env: 'testnet' | 'mainnet', configured: boolean) => void
  onWalletConfigured?: () => void
}

interface OkxWalletData {
  configured: boolean
  apiKeyMasked?: string
  maxLeverage: number
  defaultLeverage: number
  balance?: {
    total_equity: number
    available_balance: number
    unrealized_pnl: number
  }
}

// [OKX] API 基础路径
const API_BASE = '/api/okx'

export default function OkxWalletSection({
  accountId,
  accountName,
  onStatusChange,
  onWalletConfigured
}: OkxWalletSectionProps) {
  const { t } = useTranslation()

  // 钱包数据状态
  const [testnetWallet, setTestnetWallet] = useState<OkxWalletData | null>(null)
  const [mainnetWallet, setMainnetWallet] = useState<OkxWalletData | null>(null)

  // 独立加载状态
  const [loadingConfig, setLoadingConfig] = useState(false)
  const [savingTestnet, setSavingTestnet] = useState(false)
  const [savingMainnet, setSavingMainnet] = useState(false)
  const [testingTestnet, setTestingTestnet] = useState(false)
  const [testingMainnet, setTestingMainnet] = useState(false)

  // 编辑状态
  const [editingTestnet, setEditingTestnet] = useState(false)
  const [editingMainnet, setEditingMainnet] = useState(false)
  const [showTestnetKeys, setShowTestnetKeys] = useState(false)
  const [showMainnetKeys, setShowMainnetKeys] = useState(false)

  // [OKX] 表单状态 — testnet（多一个 Passphrase 字段）
  const [testnetApiKey, setTestnetApiKey] = useState('')
  const [testnetSecretKey, setTestnetSecretKey] = useState('')
  const [testnetPassphrase, setTestnetPassphrase] = useState('')  // [OKX 新增字段]
  const [testnetMaxLeverage, setTestnetMaxLeverage] = useState(20)
  const [testnetDefaultLeverage, setTestnetDefaultLeverage] = useState(1)

  // [OKX] 表单状态 — mainnet（多一个 Passphrase 字段）
  const [mainnetApiKey, setMainnetApiKey] = useState('')
  const [mainnetSecretKey, setMainnetSecretKey] = useState('')
  const [mainnetPassphrase, setMainnetPassphrase] = useState('')  // [OKX 新增字段]
  const [mainnetMaxLeverage, setMainnetMaxLeverage] = useState(20)
  const [mainnetDefaultLeverage, setMainnetDefaultLeverage] = useState(1)

  useEffect(() => {
    loadWalletInfo()
  }, [accountId])

  const loadWalletInfo = async () => {
    try {
      setLoadingConfig(true)
      const res = await fetch(`${API_BASE}/accounts/${accountId}/config`)
      if (!res.ok) return

      const data = await res.json()
      const testnetConfigured = data.testnet_configured
      const mainnetConfigured = data.mainnet_configured

      onStatusChange?.('testnet', testnetConfigured)
      onStatusChange?.('mainnet', mainnetConfigured)

      if (testnetConfigured) {
        setTestnetWallet({
          configured: true,
          apiKeyMasked: data.testnet?.api_key_masked,
          maxLeverage: data.testnet?.max_leverage || 20,
          defaultLeverage: data.testnet?.default_leverage || 1,
          balance: undefined
        })
        setTestnetMaxLeverage(data.testnet?.max_leverage || 20)
        setTestnetDefaultLeverage(data.testnet?.default_leverage || 1)
        // [OKX] 加载余额
        try {
          const balanceRes = await fetch(`${API_BASE}/accounts/${accountId}/balance?environment=testnet`)
          if (balanceRes.ok) {
            const balanceData = await balanceRes.json()
            setTestnetWallet(prev => prev ? { ...prev, balance: balanceData.balance } : null)
          }
        } catch (e) {
          console.error('Failed to load testnet balance:', e)
        }
      } else {
        setTestnetWallet(null)
      }

      if (mainnetConfigured) {
        setMainnetWallet({
          configured: true,
          apiKeyMasked: data.mainnet?.api_key_masked,
          maxLeverage: data.mainnet?.max_leverage || 20,
          defaultLeverage: data.mainnet?.default_leverage || 1,
          balance: undefined
        })
        setMainnetMaxLeverage(data.mainnet?.max_leverage || 20)
        setMainnetDefaultLeverage(data.mainnet?.default_leverage || 1)
        // [OKX] 加载余额
        try {
          const balanceRes = await fetch(`${API_BASE}/accounts/${accountId}/balance?environment=mainnet`)
          if (balanceRes.ok) {
            const balanceData = await balanceRes.json()
            setMainnetWallet(prev => prev ? { ...prev, balance: balanceData.balance } : null)
          }
        } catch (e) {
          console.error('Failed to load mainnet balance:', e)
        }
      } else {
        setMainnetWallet(null)
      }
    } catch (error) {
      console.error('Failed to load OKX config:', error)
    } finally {
      setLoadingConfig(false)
    }
  }

  // [OKX] 保存钱包（含 Passphrase）
  const handleSaveWallet = async (environment: 'testnet' | 'mainnet') => {
    const setSaving = environment === 'testnet' ? setSavingTestnet : setSavingMainnet
    const apiKey = environment === 'testnet' ? testnetApiKey : mainnetApiKey
    const secretKey = environment === 'testnet' ? testnetSecretKey : mainnetSecretKey
    const passphrase = environment === 'testnet' ? testnetPassphrase : mainnetPassphrase  // [OKX]
    const maxLev = environment === 'testnet' ? testnetMaxLeverage : mainnetMaxLeverage
    const defaultLev = environment === 'testnet' ? testnetDefaultLeverage : mainnetDefaultLeverage

    // 清理输入
    const cleanApiKey = apiKey.trim().replace(/[\s\r\n\t​-‍﻿]/g, '')
    const cleanSecretKey = secretKey.trim().replace(/[\s\r\n\t​-‍﻿]/g, '')
    const cleanPassphrase = passphrase.trim()  // [OKX] Passphrase 只需 trim

    if (!cleanApiKey || !cleanSecretKey || !cleanPassphrase) {
      toast.error('Please enter API Key, Secret Key, and Passphrase')
      return
    }

    try {
      setSaving(true)
      // [OKX] 请求体包含 passphrase 字段
      const res = await fetch(`${API_BASE}/accounts/${accountId}/setup`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          environment,
          apiKey: cleanApiKey,
          secretKey: cleanSecretKey,
          passphrase: cleanPassphrase,  // [OKX 新增字段]
          maxLeverage: maxLev,
          defaultLeverage: defaultLev
        })
      })

      const data = await res.json()

      if (res.ok && data.success !== false) {
        toast.success(`OKX ${environment} configured`)
        if (environment === 'testnet') {
          setTestnetApiKey('')
          setTestnetSecretKey('')
          setTestnetPassphrase('')  // [OKX]
          setEditingTestnet(false)
        } else {
          setMainnetApiKey('')
          setMainnetSecretKey('')
          setMainnetPassphrase('')  // [OKX]
          setEditingMainnet(false)
        }
        await loadWalletInfo()
        onWalletConfigured?.()
      } else {
        let errorMsg = data.detail || data.message || 'Failed to configure'
        toast.error(errorMsg)
      }
    } catch (error) {
      toast.error('Network error. Please check your connection and try again.')
    } finally {
      setSaving(false)
    }
  }

  const handleTestConnection = async (environment: 'testnet' | 'mainnet') => {
    const setTesting = environment === 'testnet' ? setTestingTestnet : setTestingMainnet
    try {
      setTesting(true)
      const res = await fetch(`${API_BASE}/accounts/${accountId}/balance?environment=${environment}`)
      if (res.ok) {
        const data = await res.json()
        const bal = data.balance || {}
        toast.success(`✅ Connected! Balance: $${(bal.total_equity || 0).toFixed(2)}`)
        // 更新缓存
        if (environment === 'testnet' && testnetWallet) {
          setTestnetWallet({ ...testnetWallet, balance: bal })
        } else if (environment === 'mainnet' && mainnetWallet) {
          setMainnetWallet({ ...mainnetWallet, balance: bal })
        }
      } else {
        const err = await res.json()
        toast.error(`❌ ${err.detail || 'Connection failed'}`)
      }
    } catch (error) {
      toast.error('Connection test failed')
    } finally {
      setTesting(false)
    }
  }

  const handleDeleteWallet = async (environment: 'testnet' | 'mainnet') => {
    if (!confirm(`Delete OKX ${environment} wallet?`)) return
    const setSaving = environment === 'testnet' ? setSavingTestnet : setSavingMainnet
    try {
      setSaving(true)
      const res = await fetch(`${API_BASE}/accounts/${accountId}/wallet?environment=${environment}`, {
        method: 'DELETE'
      })
      if (res.ok) {
        toast.success(`OKX ${environment} wallet deleted`)
        await loadWalletInfo()
        onWalletConfigured?.()
      }
    } catch (error) {
      toast.error('Failed to delete wallet')
    } finally {
      setSaving(false)
    }
  }

  const renderWalletBlock = (
    environment: 'testnet' | 'mainnet',
    wallet: OkxWalletData | null,
    editing: boolean,
    setEditing: (v: boolean) => void,
    apiKey: string,
    setApiKey: (v: string) => void,
    secretKey: string,
    setSecretKey: (v: string) => void,
    passphrase: string,  // [OKX 新增]
    setPassphrase: (v: string) => void,  // [OKX 新增]
    maxLev: number,
    setMaxLev: (v: number) => void,
    defaultLev: number,
    setDefaultLev: (v: number) => void,
    showKeys: boolean,
    setShowKeys: (v: boolean) => void,
    saving: boolean,
    testing: boolean,
  ) => {
    const envName = environment === 'testnet' ? 'Testnet' : 'Mainnet'
    const badgeVariant = environment === 'testnet' ? 'default' : 'destructive'

    return (
      <div className="p-4 border rounded-lg space-y-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Wallet className="h-4 w-4 text-muted-foreground" />
            <Badge variant={badgeVariant} className="text-xs">
              {environment === 'testnet' ? 'TESTNET' : 'MAINNET'}
            </Badge>
          </div>
          {wallet && !editing && (
            <div className="flex gap-2">
              <Button variant="outline" size="sm" onClick={() => setEditing(true)}>
                {t('common.edit', 'Edit')}
              </Button>
              <Button variant="destructive" size="sm" onClick={() => handleDeleteWallet(environment)} disabled={saving}>
                <Trash2 className="h-3 w-3" />
              </Button>
            </div>
          )}
        </div>

        {wallet && !editing ? (
          <div className="space-y-2">
            <div className="space-y-1">
              <label className="text-xs text-muted-foreground">API Key</label>
              <div className="flex items-center gap-2">
                <code className="flex-1 px-2 py-1 bg-muted rounded text-xs overflow-hidden">
                  {wallet.apiKeyMasked || '****'}
                </code>
                <CheckCircle className="h-4 w-4 text-green-600 flex-shrink-0" />
              </div>
            </div>

            {wallet.balance && (
              <div className="grid grid-cols-3 gap-2 text-xs">
                <div>
                  <div className="text-muted-foreground">{t('wallet.balance', 'Balance')}</div>
                  <div className="font-medium">${(wallet.balance.total_equity || 0).toFixed(2)}</div>
                </div>
                <div>
                  <div className="text-muted-foreground">{t('wallet.available', 'Available')}</div>
                  <div className="font-medium">${(wallet.balance.available_balance || 0).toFixed(2)}</div>
                </div>
                <div>
                  <div className="text-muted-foreground">PnL</div>
                  <div className={`font-medium ${(wallet.balance.unrealized_pnl || 0) >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                    ${(wallet.balance.unrealized_pnl || 0).toFixed(2)}
                  </div>
                </div>
              </div>
            )}

            <div className="grid grid-cols-2 gap-2 text-xs">
              <div>
                <div className="text-muted-foreground">{t('wallet.maxLeverage', 'Max Leverage')}</div>
                <div className="font-medium">{wallet.maxLeverage}x</div>
              </div>
              <div>
                <div className="text-muted-foreground">{t('wallet.defaultLeverage', 'Default Leverage')}</div>
                <div className="font-medium">{wallet.defaultLeverage}x</div>
              </div>
            </div>

            <Button variant="outline" size="sm" onClick={() => handleTestConnection(environment)} disabled={testing} className="w-full">
              {testing ? <><RefreshCw className="mr-2 h-3 w-3 animate-spin" />{t('wallet.testing', 'Testing...')}</> : t('wallet.testConnection', 'Test Connection')}
            </Button>
          </div>
        ) : (
          <div className="space-y-3">
            {!wallet && (
              <div className="p-2 bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded text-xs">
                <p className="text-yellow-800 dark:text-yellow-200">⚠️ No {envName.toLowerCase()} API configured.</p>
              </div>
            )}

            <div className="p-2 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded text-xs">
              <p className="text-blue-800 dark:text-blue-200">
                Get your API Key from OKX: Account → API → Create V5 API Key with Trade permission.
              </p>
            </div>

            <div className="space-y-1">
              <label className="text-xs text-muted-foreground">API Key</label>
              <Input
                type={showKeys ? 'text' : 'password'}
                value={apiKey}
                onChange={(e) => setApiKey(e.target.value)}
                placeholder="Enter your OKX API Key"
                className="font-mono text-xs h-8"
              />
            </div>

            <div className="space-y-1">
              <label className="text-xs text-muted-foreground">Secret Key</label>
              <Input
                type={showKeys ? 'text' : 'password'}
                value={secretKey}
                onChange={(e) => setSecretKey(e.target.value)}
                placeholder="Enter your OKX Secret Key"
                className="font-mono text-xs h-8"
              />
            </div>

            {/* [OKX 新增] Passphrase 输入框 */}
            <div className="space-y-1">
              <label className="text-xs text-muted-foreground">Passphrase</label>
              <div className="flex gap-2">
                <Input
                  type={showKeys ? 'text' : 'password'}
                  value={passphrase}
                  onChange={(e) => setPassphrase(e.target.value)}
                  placeholder="Enter your OKX API Passphrase"
                  className="font-mono text-xs h-8"
                />
                <Button type="button" variant="outline" size="sm" onClick={() => setShowKeys(!showKeys)} className="h-8 px-2">
                  {showKeys ? <EyeOff className="h-3 w-3" /> : <Eye className="h-3 w-3" />}
                </Button>
              </div>
              <p className="text-xs text-muted-foreground">
                The passphrase you set when creating the OKX API Key. Required for authentication.
              </p>
            </div>

            <div className="grid grid-cols-2 gap-2">
              <div className="space-y-1">
                <label className="text-xs text-muted-foreground">{t('wallet.maxLeverage', 'Max Leverage')}</label>
                <Input type="number" value={maxLev} onChange={(e) => setMaxLev(Number(e.target.value))} min={1} max={125} className="h-8 text-xs" />
              </div>
              <div className="space-y-1">
                <label className="text-xs text-muted-foreground">{t('wallet.defaultLeverage', 'Default Leverage')}</label>
                <Input type="number" value={defaultLev} onChange={(e) => setDefaultLev(Number(e.target.value))} min={1} max={maxLev} className="h-8 text-xs" />
              </div>
            </div>

            <div className="flex gap-2">
              <Button onClick={() => handleSaveWallet(environment)} disabled={saving} size="sm" className="flex-1 h-8 text-xs">
                {saving ? <><RefreshCw className="mr-2 h-3 w-3 animate-spin" />{t('wallet.saving', 'Saving...')}</> : t('wallet.saveWallet', 'Save Wallet')}
              </Button>
              {editing && (
                <Button variant="outline" onClick={() => { setEditing(false); setApiKey(''); setSecretKey(''); setPassphrase('') }} size="sm" className="h-8 text-xs">
                  {t('common.cancel', 'Cancel')}
                </Button>
              )}
            </div>
          </div>
        )}
      </div>
    )
  }

  if (loadingConfig && !testnetWallet && !mainnetWallet) {
    return (
      <div className="flex items-center justify-center py-4">
        <RefreshCw className="h-5 w-5 animate-spin text-muted-foreground" />
      </div>
    )
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mt-2">
      {/* [OKX] Testnet 钱包 */}
      {renderWalletBlock(
        'testnet', testnetWallet, editingTestnet, setEditingTestnet,
        testnetApiKey, setTestnetApiKey,
        testnetSecretKey, setTestnetSecretKey,
        testnetPassphrase, setTestnetPassphrase,  // [OKX]
        testnetMaxLeverage, setTestnetMaxLeverage,
        testnetDefaultLeverage, setTestnetDefaultLeverage,
        showTestnetKeys, setShowTestnetKeys, savingTestnet, testingTestnet,
      )}
      {/* [OKX] Mainnet 钱包 */}
      {renderWalletBlock(
        'mainnet', mainnetWallet, editingMainnet, setEditingMainnet,
        mainnetApiKey, setMainnetApiKey,
        mainnetSecretKey, setMainnetSecretKey,
        mainnetPassphrase, setMainnetPassphrase,  // [OKX]
        mainnetMaxLeverage, setMainnetMaxLeverage,
        mainnetDefaultLeverage, setMainnetDefaultLeverage,
        showMainnetKeys, setShowMainnetKeys, savingMainnet, testingMainnet,
      )}
    </div>
  )
}
