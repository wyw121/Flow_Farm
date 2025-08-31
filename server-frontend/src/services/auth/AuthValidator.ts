/**
 * 认证数据验证器
 * 负责验证用户输入数据的格式和有效性
 */

import { LoginCredentials, PasswordPolicy } from './types'

export class AuthValidator {
  private readonly passwordPolicy: PasswordPolicy

  constructor(passwordPolicy: PasswordPolicy) {
    this.passwordPolicy = passwordPolicy
  }

  /**
   * 验证登录凭证
   */
  validateLoginCredentials(credentials: LoginCredentials): {
    isValid: boolean
    errors: Record<string, string>
  } {
    const errors: Record<string, string> = {}

    // 验证标识符（用户名/邮箱/手机号）
    if (!credentials.identifier || credentials.identifier.trim().length === 0) {
      errors.identifier = '请输入用户名、邮箱或手机号'
    } else if (credentials.identifier.trim().length < 3) {
      errors.identifier = '用户名至少3个字符'
    } else if (credentials.identifier.trim().length > 50) {
      errors.identifier = '用户名不能超过50个字符'
    }

    // 验证密码
    const passwordValidation = this.validatePassword(credentials.password)
    if (!passwordValidation.isValid) {
      errors.password = passwordValidation.message
    }

    return {
      isValid: Object.keys(errors).length === 0,
      errors
    }
  }

  /**
   * 验证密码强度
   */
  validatePassword(password: string): {
    isValid: boolean
    message: string
    strength: 'weak' | 'medium' | 'strong'
  } {
    if (!password) {
      return {
        isValid: false,
        message: '请输入密码',
        strength: 'weak'
      }
    }

    // 检查长度
    if (password.length < this.passwordPolicy.minLength) {
      return {
        isValid: false,
        message: `密码至少${this.passwordPolicy.minLength}个字符`,
        strength: 'weak'
      }
    }

    if (password.length > 128) {
      return {
        isValid: false,
        message: '密码不能超过128个字符',
        strength: 'weak'
      }
    }

    const issues: string[] = []
    let strengthScore = 0

    // 检查大写字母
    if (this.passwordPolicy.requireUppercase && !/[A-Z]/.test(password)) {
      issues.push('至少包含一个大写字母')
    } else if (/[A-Z]/.test(password)) {
      strengthScore++
    }

    // 检查小写字母
    if (this.passwordPolicy.requireLowercase && !/[a-z]/.test(password)) {
      issues.push('至少包含一个小写字母')
    } else if (/[a-z]/.test(password)) {
      strengthScore++
    }

    // 检查数字
    if (this.passwordPolicy.requireNumbers && !/\d/.test(password)) {
      issues.push('至少包含一个数字')
    } else if (/\d/.test(password)) {
      strengthScore++
    }

    // 检查特殊字符
    const specialCharRegex = /[!@#$%^&*()_+\-={}";':\\|,.<>?]/
    if (this.passwordPolicy.requireSpecialChars && !specialCharRegex.test(password)) {
      issues.push('至少包含一个特殊字符')
    } else if (specialCharRegex.test(password)) {
      strengthScore++
    }

    // 额外的强度检查
    if (password.length >= 12) strengthScore++
    if (/(.)\1{2,}/.test(password)) strengthScore-- // 连续相同字符降分

    const isValid = issues.length === 0
    let strength: 'weak' | 'medium' | 'strong' = 'weak'

    if (isValid) {
      if (strengthScore >= 4) {
        strength = 'strong'
      } else if (strengthScore >= 2) {
        strength = 'medium'
      }
    }

    return {
      isValid,
      message: isValid ? '密码强度符合要求' : issues.join('，'),
      strength
    }
  }

  /**
   * 验证邮箱格式
   */
  validateEmail(email: string): boolean {
    if (!email) return false

    const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/
    return emailRegex.test(email)
  }

  /**
   * 验证手机号格式（中国大陆）
   */
  validatePhone(phone: string): boolean {
    if (!phone) return false

    // 中国大陆手机号正则
    const phoneRegex = /^1[3-9]\d{9}$/
    return phoneRegex.test(phone)
  }

  /**
   * 验证用户名格式
   */
  validateUsername(username: string): {
    isValid: boolean
    message: string
  } {
    if (!username) {
      return {
        isValid: false,
        message: '请输入用户名'
      }
    }

    if (username.length < 3) {
      return {
        isValid: false,
        message: '用户名至少3个字符'
      }
    }

    if (username.length > 30) {
      return {
        isValid: false,
        message: '用户名不能超过30个字符'
      }
    }

    // 用户名只能包含字母、数字、下划线和连字符
    if (!/^[a-zA-Z0-9_-]+$/.test(username)) {
      return {
        isValid: false,
        message: '用户名只能包含字母、数字、下划线和连字符'
      }
    }

    // 不能以数字开头
    if (/^\d/.test(username)) {
      return {
        isValid: false,
        message: '用户名不能以数字开头'
      }
    }

    return {
      isValid: true,
      message: '用户名格式正确'
    }
  }

  /**
   * 检测登录标识符类型
   */
  detectIdentifierType(identifier: string): 'username' | 'email' | 'phone' | 'unknown' {
    if (!identifier) return 'unknown'

    const trimmed = identifier.trim()

    if (this.validateEmail(trimmed)) {
      return 'email'
    }

    if (this.validatePhone(trimmed)) {
      return 'phone'
    }

    if (this.validateUsername(trimmed).isValid) {
      return 'username'
    }

    return 'unknown'
  }

  /**
   * 清理和标准化输入
   */
  sanitizeInput(input: string): string {
    if (!input) return ''

    return input.trim().replace(/\s+/g, ' ')
  }

  /**
   * 验证确认密码
   */
  validatePasswordConfirmation(password: string, confirmPassword: string): {
    isValid: boolean
    message: string
  } {
    if (!confirmPassword) {
      return {
        isValid: false,
        message: '请确认密码'
      }
    }

    if (password !== confirmPassword) {
      return {
        isValid: false,
        message: '两次输入的密码不一致'
      }
    }

    return {
      isValid: true,
      message: '密码确认正确'
    }
  }

  /**
   * 检查常见弱密码
   */
  isCommonPassword(password: string): boolean {
    const commonPasswords = [
      '123456', 'password', '123456789', '12345678',
      'abc123', 'qwerty', 'admin', 'letmein',
      'welcome', 'monkey', '1234567890', 'password123'
    ]

    return commonPasswords.includes(password.toLowerCase())
  }

  /**
   * 生成密码强度提示
   */
  getPasswordStrengthTips(): string[] {
    const tips: string[] = []

    if (this.passwordPolicy.minLength > 6) {
      tips.push(`至少${this.passwordPolicy.minLength}个字符`)
    }

    if (this.passwordPolicy.requireUppercase) {
      tips.push('包含大写字母')
    }

    if (this.passwordPolicy.requireLowercase) {
      tips.push('包含小写字母')
    }

    if (this.passwordPolicy.requireNumbers) {
      tips.push('包含数字')
    }

    if (this.passwordPolicy.requireSpecialChars) {
      tips.push('包含特殊字符')
    }

    return tips
  }
}
