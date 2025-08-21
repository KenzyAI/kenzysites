import winston from 'winston'
import DailyRotateFile from 'winston-daily-rotate-file'
import path from 'path'

const { combine, timestamp, printf, colorize, errors } = winston.format

// Custom log format
const logFormat = printf(({ level, message, timestamp, stack, ...metadata }) => {
  let msg = `${timestamp} [${level}]: ${message}`

  if (Object.keys(metadata).length > 0) {
    msg += ` ${JSON.stringify(metadata)}`
  }

  if (stack) {
    msg += `\n${stack}`
  }

  return msg
})

// Development logger configuration
const developmentLogger = () => {
  return winston.createLogger({
    level: 'debug',
    format: combine(
      colorize(),
      timestamp({ format: 'YYYY-MM-DD HH:mm:ss' }),
      errors({ stack: true }),
      logFormat
    ),
    transports: [
      new winston.transports.Console({
        stderrLevels: ['error'],
      }),
    ],
  })
}

// Production logger configuration
const productionLogger = () => {
  return winston.createLogger({
    level: 'info',
    format: combine(
      timestamp({ format: 'YYYY-MM-DD HH:mm:ss' }),
      errors({ stack: true }),
      logFormat
    ),
    transports: [
      // Console transport for production
      new winston.transports.Console({
        stderrLevels: ['error'],
      }),

      // File transport for all logs
      new DailyRotateFile({
        filename: path.join('logs', 'application-%DATE%.log'),
        datePattern: 'YYYY-MM-DD',
        zippedArchive: true,
        maxSize: '20m',
        maxFiles: '14d',
        level: 'info',
      }),

      // Separate file for errors
      new DailyRotateFile({
        filename: path.join('logs', 'error-%DATE%.log'),
        datePattern: 'YYYY-MM-DD',
        zippedArchive: true,
        maxSize: '20m',
        maxFiles: '30d',
        level: 'error',
      }),
    ],
  })
}

// Create logger based on environment
const logger = process.env.NODE_ENV === 'production' ? productionLogger() : developmentLogger()

// Utility functions for structured logging
export const logInfo = (message: string, meta?: Record<string, unknown>) => {
  logger.info(message, meta)
}

export const logError = (
  message: string,
  error?: Error | unknown,
  meta?: Record<string, unknown>
) => {
  if (error instanceof Error) {
    logger.error(message, { ...meta, error: error.message, stack: error.stack })
  } else {
    logger.error(message, { ...meta, error })
  }
}

export const logWarn = (message: string, meta?: Record<string, unknown>) => {
  logger.warn(message, meta)
}

export const logDebug = (message: string, meta?: Record<string, unknown>) => {
  logger.debug(message, meta)
}

// API request logging middleware
export const logRequest = (method: string, path: string, statusCode: number, duration: number) => {
  const level = statusCode >= 500 ? 'error' : statusCode >= 400 ? 'warn' : 'info'
  logger.log(level, `${method} ${path} ${statusCode} ${duration}ms`)
}

// Database query logging
export const logQuery = (query: string, duration: number) => {
  logger.debug(`Database Query (${duration}ms): ${query}`)
}

// AI API logging
export const logAIRequest = (provider: string, model: string, tokens: number, duration: number) => {
  logger.info(`AI Request`, { provider, model, tokens, duration })
}

export default logger
