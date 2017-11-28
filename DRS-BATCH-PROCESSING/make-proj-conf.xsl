<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xs="http://www.w3.org/2001/XMLSchema" exclude-result-prefixes="xs" version="2.0">
    <xsl:param name="hId" as="xs:string" required="yes"/>
    <xsl:template match="property[@name='alephID']">
        <xsl:copy>
            <xsl:apply-templates select="@*"/>
            <xsl:attribute name="value">
                <xsl:value-of select="$hId"/>
            </xsl:attribute>
        </xsl:copy>
    </xsl:template>
    <xsl:template match="property[@name='harvardMetadataLinks']">
        <xsl:copy>
            <xsl:apply-templates select="@*"/>
            <xsl:attribute name="value">
                <xsl:value-of select="replace(@value, 'hollis-id', $hId)"/>
            </xsl:attribute>
        </xsl:copy>
    </xsl:template>
    <xsl:template match="@*|node()">
        <xsl:copy>
            <xsl:apply-templates select="@*|node()"/>
        </xsl:copy>
    </xsl:template>
</xsl:stylesheet>
